import argparse
import json
from multiprocessing import Lock, Process, Queue, current_process
import multiprocessing
import os
import time
import queue
import sys
import errno
import traceback

from GromacsMetadataExtractor import MetadataExtractor # imported for using queue.Empty exception

# python3 paralel_run.py --data=zenodo_export_results/all-zenodo-tpr-2023-09.txt --data_dir=metadata-data --output=exported-metadata-2023-09.json

def load_argumets():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data',
                        type=str,
                        help='Data file (Obligatory argument)',
                        required=True)
    parser.add_argument('--data_dir',
                        type=str,
                        help='Output dir. (Obligatory argument)')
    parser.add_argument('--output',
                        type=str,
                        help='Output dir. (Obligatory argument)')

    args = parser.parse_args()
    if not os.path.isfile(args.data):
        exit(f"\nERROR! There is no file {args.data}!\n")

    return args

def do_job(pid, tasks_to_accomplish, tasks_that_are_done, queues_status):
    cnt = 1
    while True:
        try:
            '''
                try to get task from the queue. get_nowait() function will
                raise queue.Empty exception if the queue is empty.
                queue(False) function would do the same task also.
            '''
            task = tasks_to_accomplish.get()
            metadata = dict()
            queues_status[pid]["current_job"] = task["file_location"]
            try:
                metadata = MetadataExtractor(task["file_location"], task["file_location"], None, False).run().export()
            except BaseException as e:
                print(e)
                ex_type, ex_value, ex_traceback = sys.exc_info()
                # print("Job failed on")
                metadata = {
                    "state": "failed",
                    "error_message": "Error type: {}, message: {}, stack: {}".format(ex_type.__name__, ex_value, traceback.extract_tb(ex_traceback)),
                }
                # queues_status[pid]["status"] = "finished"
        except IOError as e:
            if e.errno == errno.EPIPE:
                current_process().terminate()
                break
        except EOFError as e:
            print("Queue {} is empty".format(pid))
        except queue.Empty:
            queues_status[pid]["status"] = "finished"
            current_process().terminate()
            break
        else:
            '''
                if no exception has been raised, add the task completion
                message to task_that_are_done queue
            '''
            cnt+=1
            # print("Progress of proc ",  tasks_that_are_done.qsize(), "/", tasks_to_accomplish.qsize(), task["file_location"])
            metadata["_record_created"] = task["record_created"]
            metadata["_record_file"] = task["filename"]
            metadata["_record_id"] = task["record_id"]
            metadata["_record_url"] = task["url"]
            tasks_that_are_done.put(metadata)
            queues_status[pid]["last_job"] = task["file_location"]
            queues_status[pid]["accomplished"] += 1

    return True

def progressbar(it, prefix="", size=60, out=sys.stdout): # Python3.3+
    count = len(it)
    def show(j):
        x = int(size*j/count)
        print("{}[{}{}] {}/{}".format(prefix, "#"*x, "."*(size-x), j, count),
                end='\r', file=out, flush=True)
    show(0)
    for i, item in enumerate(it):
        yield item
        show(i+1)
    print("\n", flush=True, file=out)

def do_dump(data):
    return json.dumps(data)

def main():
    # multiprocessing.set_start_method('spawn')
    number_of_processes = 30
    tasks_to_accomplish = multiprocessing.Manager().Queue()
    tasks_that_are_done = multiprocessing.Manager().Queue()
    queues_status = multiprocessing.Manager().dict()

    args = load_argumets()

    with open(args.data, 'r') as f:
        data = json.loads(f.read())

    cnt = 0
    for record in data:
        for url in record["files"]:
            cnt += 1
            record["metadata"] = list()
            tpr_dir = os.path.join(args.data_dir, record["created"][0:4], record["id"])
            filename = url.rsplit("/")[-1]
            file_location = os.path.join(tpr_dir, filename)
            task = {
                "record_id": record["id"],
                "record_created": record["created"],
                "url": url,
                "filename": filename,
                "file_location": file_location
            }
            tasks_to_accomplish.put(task)
    print("Total jobs in queue: ", tasks_to_accomplish.qsize())
    total_tasks = tasks_to_accomplish.qsize()
    results = []
    # with multiprocessing.Pool(processes=10, maxtasksperchild=1) as pool:
    #     results = pool.starmap(do_job, tasks_to_accomplish)
    #     pool.terminate()
    #     pool.join()

    processes = [[w, Process(target=do_job, args=(w, tasks_to_accomplish, tasks_that_are_done, queues_status))] for w in range(number_of_processes)]

    for proc in processes:
        time.sleep(1)
        queues_status[proc[0]] = {"status": "started", "last_job": "", "accomplished": 0, "current_job": ""}
        proc[1].start()

    while not tasks_that_are_done.qsize() == total_tasks:
            print("[{}] Tasks in queue: {}, accomplished {}, results {}".format(time.strftime("%y-%m-%d %H:%M:%S", time.localtime()), tasks_to_accomplish.qsize(), tasks_that_are_done.qsize(), len(results)))
            # for p in processes:
            #     print("Process {} ({}) - current: {} - last: {}".format(p[0], queues_status[p[0]]["status"], queues_status[p[0]]["current_job"], queues_status[p[0]]["last_job"]))
            # print("Working on it", end="\r", flush=True)
            time.sleep(5)

    print("------------ All tasks has been processed ---------------")

    while tasks_that_are_done.qsize():
        results.append(tasks_that_are_done.get())

    print("------------ Results gathered ---------------")
    print("Total jobs in queue:      {}", total_tasks)
    print("Total records gathered:   {}", len(results))

    for p in processes:
        if queues_status[proc[0]]["status"] == "finished":
            proc[1].join(1)

    print("------------ All processes joined ---------------")

    metadata_chunks = []
    n = 50
    metadata_chunks = [results[i:i + n] for i in range(0, len(results), n)]

    metadata_result = []
    with multiprocessing.Pool(processes=10) as pool:
        metadata_result = pool.map(do_dump, metadata_chunks)
        pool.terminate()
        pool.join()

    print("------------ Results formated as JSON ---------------")

    print("------------ All tasks has been completed ---------------")
    print("Total jobs in queue:      {}", total_tasks)
    print("Lenght of the results:    {}".format(str(len(results))))
    print("Count of tasks:           {}".format(str(cnt)))
    print("# of chunks for results:  {}".format(str(len(metadata_chunks))))
    print("# of records to output:   {}".format(str(len(metadata_result))))

    print("------------ Results written to the file  as '{}' ---------------".format(args.output))

    with open(args.output, 'w') as f:
        f.write("{}".format(", ".join(metadata_result)))

    # # print the output
    # while not tasks_that_are_done.empty():
    #     t = tasks_that_are_done.get()
    #     aall_records.append(t)
    #     with open(args.output, 'a') as f:
    #         f.write(json.dumps(t))
        # print(t["file_location"])

    # print(json.dumps(aall_records))

    return True


if __name__ == '__main__':
    main()