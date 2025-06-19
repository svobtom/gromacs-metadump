import { Alert, Button, Grid, Paper, Skeleton, Stack, Typography } from "@mui/material"
import { useEffect, useState } from "react"
import { useNavigate, useParams } from "react-router-dom"
import FilePreview from "../Components/FilePreview"
import DownloadMetadataActions from "../Components/DownloadMetadata"
import { set } from "yaml/dist/schema/yaml-1.1/set"
import SessionStatus from "../Components/SessionStatus"

type FileType = 'tpr' | 'gro' | 'top' | 'opt';

export interface AnnotationResultsStatusResponse {
    uuid: string
    status: 'pending' | 'processing' | 'completed' | 'failed'
    processed_files: {
        [key: string]: string
    }
    created: string
    expires: string
    options: {
        [key: string]: any}
    error?: string
}

const AnnotationResults = () => {

    const navigate = useNavigate();

    const { session } = useParams<{ session: string }>()
    
    const [loading, setLoading] = useState(true)
    const [data, setData] = useState<Object>({})
    const [statedata, setStateData] = useState<AnnotationResultsStatusResponse>({
        uuid: '',
        processed_files: {},
        status: 'pending',
        created: '',
        expires: '',
        options: {}
        
    })
    const [error, setError] = useState<any>(null)

    useEffect(() => {

        (async function fetchStatus() {
            try {
                const response = await fetch(`/api/annotate/${session}`);
                if (!response.ok) {
                    if (response.status === 404) {
                        throw new Error(`Session ${session} not found`);
                    }
                    if (response.status === 400) {
                        throw new Error(`Session ${session} is not ready yet`);
                    }
                    if (response.status === 500) {
                        throw new Error(`Server error, try again.`);
                    }
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const data = await response.json();
                setStateData(data);
                if (data.status === 'pending' || data.status === 'processing') {
                    setTimeout(fetchStatus, 5000);
                }
            } catch (error) {
                setError(error);
            }
        })();
    }, [session])

    useEffect(() => {
        if (statedata.status === 'completed') {
            setLoading(false)
            fetch(`/api/annotate/${session}/results`)
            .then(response => {
                if (!response.ok) {
                    if (response.status === 404) {
                        throw new Error(`Session ${session} not found`)
                    }
                    if (response.status === 400) {
                        throw new Error(`Session ${session} is not ready yet`)
                    }
                    if (response.status === 500) {
                        throw new Error(`Server error, try again.`)
                    }
                    throw new Error(`HTTP error! status: ${response.status} ${response.text}`);
                }
                return response.json()
            })
            .then(data => setData(data))
            .catch(error => setError(error))
        } else if (statedata.status === 'failed') {
            setLoading(false)
            setError(new Error(`Session ${session} failed`))
        }
    }, [statedata])


    const handleViewAnnotations = () => {
        navigate(`/results/${session}/view`, { state: { data: data, stateData: statedata } })
    }

    const fileTypesMetadata: Record<FileType, { title: string; description: string }> = {
        tpr: {title: "GROMACS TPR", description: "The run input file for GROMACS simulations"},
        gro: {title: "GROMACS GRO", description: "The run output file for GROMACS simulations"},
        top: {title: "GROMACS TOP", description: "The topology file for GROMACS simulations"},
        opt: {title: "GROMACS OPT", description: "The optional metadata"},
    }

    const optionalFileTypes: FileType[] = ['tpr', 'gro', 'top', 'opt']
    console.log(error)
    return (
        <>
            {error && <Alert sx={{mb: 3}} severity="error">
                        {error.message}
                      </Alert>}
                        {/* <Paper sx={{ p: 2, display: "flex", mb: 3}}> */}
                            <Stack direction="column" sx={{width: "100%"}} spacing={5} alignItems="stretch" whiteSpace={"pre-line"}>
                                <Stack direction="column" spacing={1}>
                                    <Typography variant="h1">Annotation results</Typography>
                                    <Typography>Session ID: {session}</Typography>
                                    <Typography>Job status: <SessionStatus>{statedata?.status || ""}</SessionStatus></Typography>
                                    <Typography>Session Creation: {(new Date(statedata?.created)).toLocaleString()}</Typography>
                                    <Typography>Session Expiration: {(new Date(statedata?.expires)).toLocaleString()}</Typography>
                                </Stack>
                                {loading || error ? (
                                    skeleton
                                ) : (
                                    <>
                                    <Typography variant="h2">Files provided</Typography>
                                    <Grid container spacing={1} alignItems="stretch">
                                        {optionalFileTypes.map((fileType: FileType) => (
                                            <Grid item xs={12} sm={6} md={3} key={fileType}>
                                                <FilePreview 
                                                    fileType={fileTypesMetadata[fileType].title} 
                                                    description={fileTypesMetadata[fileType].description}
                                                    file={statedata.processed_files?.[fileType] || ""} 
                                                    isUploaded={!!statedata?.processed_files?.[fileType] || false} 
                                                />
                                            </Grid>
                                        ))}
                                    </Grid>
                                    <Stack direction="row" justifyItems={"left"} spacing={1}>
                                    <DownloadMetadataActions stateData={statedata} data={data} />
                                    <Button size="large" variant="outlined" color="primary" sx={{ mt: 0 }} onClick={handleViewAnnotations}>
                                        View Annotations
                                    </Button>
                                    </Stack>
                                    </>
                                )}
                            </Stack>
                        {/* </Paper> */}
        </>
    )
}

const skeleton = (
    <Stack direction="column" sx={{width: "100%"}} spacing={5} alignItems="stretch" whiteSpace={"pre-line"}>
    <Stack direction="column" spacing={1}>
        <Skeleton variant="text" width="60%" />
        <Skeleton variant="text" width="40%" />
        <Skeleton variant="text" width="50%" />
    </Stack>
    <Grid container spacing={1} alignItems="stretch">
        {[...Array(3)].map((_, index) => (
            <Grid item xs={12} sm={6} md={4} key={index}>
                <Skeleton variant="rectangular" height={118} />
            </Grid>
        ))}
    </Grid>
    <Stack direction="row" justifyItems={"left"} spacing={1}>
        <Skeleton variant="rectangular" width={150} height={40} />
        <Skeleton variant="rectangular" width={150} height={40} />
    </Stack>
    </Stack>
)

export default AnnotationResults