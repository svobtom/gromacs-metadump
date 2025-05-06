import { Alert, Button, Grid, Paper, Skeleton, Stack, Typography } from "@mui/material"
import { useEffect, useState } from "react"
import { useNavigate, useParams } from "react-router-dom"
import FilePreview from "../Components/FilePreview"
import DownloadMetadataActions from "../Components/DownloadMetadata"

export interface AnnotationResultsResponse {
    request_id: string
    result: Object
    uploaded_files: {
        tpr?: string
        gro?: string
        top?: string
        custom?: string
    }
    job_metadata: {
        status: 'queued' | 'running' | 'completed' | 'failed'
        error?: string
    }

}

const AnnotationResults = () => {

    const navigate = useNavigate();

    const { session } = useParams<{ session: string }>()
    
    const [loading, setLoading] = useState(true)
    const [data, setData] = useState<AnnotationResultsResponse>({
        request_id: '',
        result: {},
        uploaded_files: {},
        job_metadata: {
            status: 'queued'
        }
    })
    const [error, setError] = useState<any>(null)

    useEffect(() => {

        fetch(`https://gmxmetadump.biodata.ceitec.cz/api/annotate/${session}`)
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
        .finally(() => setLoading(false))
    }, [session])

    const handleViewAnnotations = () => {
        navigate(`/results/${session}/view`, { state: { data: data } })
    }

    const fileTypesMetadata = {
        tpr: {title: "GROMACS TPR", description: "The run input file for GROMACS simulations"},
        gro: {title: "GROMACS GRO", description: "The run output file for GROMACS simulations"},
        top: {title: "GROMACS TOP", description: "The topology file for GROMACS simulations"},
        custom: {title: "Optional Annotations", description: "An optional metadata input provided by the user"}
    }
    const optionalFileTypes: Array<keyof AnnotationResultsResponse['uploaded_files']> = ['tpr', 'gro', 'top', 'custom']
    console.log(error)
    return (
        <>
            {error && <Alert sx={{mb: 3}} severity="error">
                        {error.message}
                      </Alert>}
                      {loading || error ? (
                        <Paper sx={{ p: 2, display: "flex", mb: 3}}>
                            {skeleton}
                        </Paper>
                      ) : (
                        // <Paper sx={{ p: 2, display: "flex", mb: 3}}>
                            <Stack direction="column" sx={{width: "100%"}} spacing={5} alignItems="stretch" whiteSpace={"pre-line"}>
                                <Stack direction="column" spacing={1}>
                                    <Typography variant="h1">Annotation results</Typography>
                                    <Typography>Session: {session}</Typography>
                                    <Typography>Job status: {data?.job_metadata?.status || ""}</Typography>
                                    <Typography>Session Expiration: {new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toLocaleDateString()}</Typography>
                                </Stack>
                                <Typography variant="h2">Files provided</Typography>
                                <Grid container spacing={1} alignItems="stretch">
                                    {optionalFileTypes.map((fileType) => (
                                        <Grid item xs={12} sm={6} md={3} key={fileType}>
                                            <FilePreview 
                                                fileType={fileTypesMetadata[fileType].title} 
                                                description={fileTypesMetadata[fileType].description}
                                                file={data?.uploaded_files?.[fileType] || ""} 
                                                isUploaded={!!data?.uploaded_files?.[fileType] || false} 
                                            />
                                        </Grid>
                                    ))}
                                </Grid>
                                <Stack direction="row" justifyItems={"left"} spacing={1}>
                                <DownloadMetadataActions data={data} />
                                <Button size="large" variant="outlined" color="primary" sx={{ mt: 0 }} onClick={handleViewAnnotations}>
                                    View Annotations
                                </Button>
                                </Stack>
                            </Stack>
                        // </Paper>
                      )}
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