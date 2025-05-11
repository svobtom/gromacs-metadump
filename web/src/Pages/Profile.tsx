import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import { useState, useEffect } from 'react';
import Sessions, { AnnotationSessionRecord } from '../Components/Sessions';
import { Box, Stack, Typography } from '@mui/material';

export interface UserProfile {
    name: string;
    orcid: string;
    organization: string;
    sessions: AnnotationSessionRecord[];
}

const Profile: React.FC = () => {
    const [profile, setProfile] = useState<UserProfile>({
        name: '',
        orcid: '',
        organization: '',
        sessions: [],
    });

    useEffect(() => {
        var storedProfile = localStorage.getItem('userProfile');
        if (storedProfile) {
            const parsedProfile = JSON.parse(storedProfile);
            parsedProfile.sessions = JSON.parse(localStorage.getItem('request_ids') || '[]');
            setProfile(parsedProfile);
        }
    }, []);

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        setProfile({ ...profile, [name]: value });
    };

    const handleSave = () => {
        localStorage.setItem('userProfile', JSON.stringify(profile));
    };

    const handleRemoveProfile = () => {
        localStorage.removeItem('userProfile');
        setProfile({
            name: '',
            orcid: '',
            organization: '',
            sessions: [],
        });
    }        

    return (
        <Box>
            <Stack direction={"column"} spacing={2}>
                <Box>
                    <Typography variant="h1">User Profile</Typography>
                    <Typography variant="body1">Edit your profile information</Typography>
                    <Typography variant="body1">This information will be used to generate the metadata</Typography>
                    <Stack direction="row" spacing={2} sx={{mt: 2}}>
                        <TextField
                            label="Name"
                            name="name"
                            value={profile.name}
                            onChange={handleInputChange}
                            variant="outlined"
                            margin="normal"
                            sx={{ width: "25%" }}
                            />
                        <TextField
                            label="ORCID"
                            name="orcid"
                            value={profile.orcid}
                            onChange={handleInputChange}
                            variant="outlined"
                            margin="normal"
                            sx={{ width: "25%" }}
                            />
                    </Stack>
                    <TextField
                            label="Organization"
                            name="organization"
                            value={profile.organization}
                            onChange={handleInputChange}
                            variant="outlined"
                            margin="normal"
                            sx={{ width: "50%" }}
                            />
                    <Stack direction="row" spacing={2}>
                        <Button variant="contained" color="primary" onClick={handleSave}>
                            Save
                        </Button>
                        <Button variant="contained" color="secondary" onClick={handleRemoveProfile}>
                            Remove
                        </Button>
                    </Stack>
                </Box>
                <Box>
                    <Sessions />
                </Box>
            </Stack>
        </Box>
    );
};

export default Profile;