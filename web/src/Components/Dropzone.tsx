import { FileUpload } from "@mui/icons-material";
import { Box, Paper, Stack, Typography } from "@mui/material";
import { useEffect } from "react";
import { FileWithPath, useDropzone } from "react-dropzone";
import { Dispatch, SetStateAction } from "react";

interface DropzoneProps {
    setUploadedFiles: Dispatch<SetStateAction<FileWithPath[]>>;
    setUploaded: Dispatch<SetStateAction<boolean>>;
}

const Dropzone = ({ setUploadedFiles, setUploaded }: DropzoneProps) => {    const {
        acceptedFiles,
        fileRejections,
        getRootProps,
        getInputProps
    } = useDropzone({
        accept: {
            'application/octet-stream': [".tpr", ".gro", ".top"],
            'application/json': [".custom-metadata"],
            // 'text/yaml': [".yaml"],
            'archive/zip': [".zip"],
            'archive/x-tar': [".tar"]
            
        }
    });

    useEffect(() => {
        if (acceptedFiles.length > 0) {
            setUploadedFiles((state: FileWithPath[]) => state.concat(acceptedFiles))
        } else {
            // setUploaded(false)
        }
    }, [acceptedFiles])

    
    return (
        <Stack direction="column" spacing={5}>
            <Box>
                <Stack direction="column" spacing={1}>
                    <Paper elevation={0} sx={{ p: 5, textAlign: "center", border: "2.5px dashed", "&:hover": { borderColor: "#F47D20", cursor: "pointer" } }} variant="outlined" >
                        <div {...getRootProps({ className: 'dropzone' })}>
                            <input {...getInputProps()} />
                            <FileUpload sx={{ fontSize: "7em", color: "#F47D20" }} />
                            <Typography variant="h3">Upload files here</Typography>
                            {/* or archives *.zip or *.tar(.gz) */}
                            <Typography variant="subtitle1"><em>(Only [*.tpr *.gro and *.top or archives containing those files *.zip and *.tar(.gz)] are accepted)</em></Typography>
                        </div>
                    </Paper>
                </Stack>
            </Box>
        </Stack>
    );
}


export default Dropzone;
