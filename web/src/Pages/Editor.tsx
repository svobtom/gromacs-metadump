import { useEffect, useState } from "react"
import { useLocation, useNavigate, useParams } from 'react-router-dom'
import { Alert, Button, Grid, IconButton, Stack, Tooltip, Typography } from "@mui/material"
import FormsWrapped from "../Components/FormsWrapper"
import schema from "../schemas/gmx-native.scheme.json"
import uischema from "../schemas/gmx-native.ui.scheme.json"
// import ProteinViewer from "../Components/ProteinViewer"
import { ErrorObject } from 'ajv'
import DownloadMetadataActions from "../Components/DownloadMetadata"
import { AnnotationResultsStatusResponse } from "./AnnotationResults"
import { ArrowBack } from "@mui/icons-material"


const Editor = () => {
    const location = useLocation()
    const navigate = useNavigate()

    const { session } = useParams<{ session: string }>()
    
    const sourceData = location.state?.data as Object
    const stateData = location.state?.stateData as AnnotationResultsStatusResponse
    const [data, setData] = useState<Object>(sourceData)

    const [formErrors, setFormErrors] = useState<ErrorObject[] | undefined>(undefined)


    useEffect(() => {
        if (!sourceData) {
            navigate(`/results/${session}`)
        }
        setData(sourceData)
    }, [sourceData, navigate, session])

    if (!data)
        return

    return (
        // <Paper sx={{ p: 2, display: "flex", mb: 3}}>
            <Grid container justifyContent="space-between" position="relative" spacing={3}>
                <Grid item xs={12} sm={12} md={9} lg={8} xl={8}>
                    <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 3 }}>
                        <Tooltip title="Back to results">
                            <IconButton onClick={() => navigate(-1)} size="large">
                                <ArrowBack />
                            </IconButton>
                        </Tooltip>
                        <Typography variant="h1" sx={{ mb: 3 }}>Annotations</Typography>
                    </Stack>
                    {sourceData !== data && (
                    <Alert sx={{mb: 3}} severity="warning" action={
                        <Button variant="outlined" color="error" size="small" onClick={() => {
                            setData(sourceData)
                            setFormErrors(undefined)
                        }
                        }>Reset</Button>
                    }>
                        
                        <Typography variant="h3">Be carefull. You have made changes to the metadata annotations.</Typography>
                    </Alert>
                    )}
                    <FormsWrapped schema={schema} uischema={uischema} data={data} setData={setData} setErrors={setFormErrors} />
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
                        <DownloadMetadataActions data={data} stateData={stateData} mode="advanced" />
                    {/* </Paper> */}
                    </Grid>   
                {/* <ProteinViewer pdbData={location.state?.pdbData ?? ""} uniprotId={uniprotId} width={500} height={500} /> */}
            </Grid>
        // </Paper>
    )
}

export default Editor
