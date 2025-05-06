import { useEffect, useState } from "react"
import { useLocation, useNavigate, useParams } from 'react-router-dom'
import { Stack, Grid, Typography, Paper } from "@mui/material"
import FormsWrapped from "../Components/FormsWrapper"
import schema from "../schemas/gmx-native.scheme.json"
import uischema from "../schemas/gmx-native.ui.scheme.json"
// import ProteinViewer from "../Components/ProteinViewer"
import { ErrorObject } from 'ajv'
import { AnnotationResultsResponse } from "./AnnotationResults"
import DownloadMetadataActions from "../Components/DownloadMetadata"


const Editor = () => {
    const location = useLocation()
    const navigate = useNavigate()

    const { session } = useParams<{ session: string }>()
    
    const data = location.state?.data as AnnotationResultsResponse
    const metadata: Object = data?.result

    const [formErrors, setFormErrors] = useState<ErrorObject[] | undefined>(undefined)


    useEffect(() => {
        if (!metadata) {
            navigate(`/results/${session}`)
        }
    }, [metadata, navigate, session])

    if (!data)
        return

    return (
        // <Paper sx={{ p: 2, display: "flex", mb: 3}}>
            <Grid container justifyContent="space-between" position="relative" spacing={3}>
                <Grid item xs={12} sm={12} md={9} lg={8} xl={8}>
                    <Typography variant="h1" sx={{ mb: 3 }}>Annotations</Typography>
                    <FormsWrapped schema={schema} uischema={uischema} data={metadata} setData={() => {}} setErrors={setFormErrors} />
                        {/* {formErrors && formErrors.length > 0 && 
                            <Stack direction="column" spacing={1} sx={{mt: 3, mb: 3}} color="red">
                                <Typography variant="h3">Errors</Typography>
                                <ul>
                                    {formErrors.map((error: ErrorObject, index) => {
                                        // For some reason `error.instancePath` was crashing my build
                                        // so I had to stringify and parse it to get the value :(
                                        const err = JSON.parse(JSON.stringify(error));
                                        return(
                                            <li key={index}>{err.instancePath}: {err.message}</li>
                                        )}
                                    )}
                                </ul>
                            </Stack>
                        } */}
                </Grid>
                    <Grid item xs={12} sm={12} md={3} lg={4} xl={4} justifyContent={"flex-end"} alignItems={"center"}> 
                    {/* <Paper sx={{ p: 2, display: "flex", flexDirection: "column", height: "100%" }}> */}
                        <Typography variant="h1" sx={{ mb: 3 }}>Download</Typography>
                        <DownloadMetadataActions data={data} mode="advanced" />
                    {/* </Paper> */}
                    </Grid>   
                {/* <ProteinViewer pdbData={location.state?.pdbData ?? ""} uniprotId={uniprotId} width={500} height={500} /> */}
            </Grid>
        // </Paper>
    )
}

export default Editor
