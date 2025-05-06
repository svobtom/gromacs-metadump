import './App.css';
import { ThemeProvider } from '@emotion/react';
import { CssBaseline, createTheme } from '@mui/material';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './Components/Layout';
import Frontpage from './Pages/Frontpage';
import Editor from './Pages/Editor';
import AnnotationResults from './Pages/AnnotationResults';
import Profile from './Pages/Profile';

function App() {

  const theme = createTheme({
    palette: {
      mode: "light",
      primary: {
        main: "#F47D20"
      },
      secondary: {
        main: "#1A1A1A"
      },
    },
    components: {
      MuiTypography: {
        defaultProps: {
          variantMapping: {
            h1: 'h1',
            h2: 'h2',
            h3: 'h3',
            h4: 'h1',
            h5: 'h1',
            h6: 'h1',
            subtitle1: 'h3',
            subtitle2: 'h3',
            body1: 'span',
            body2: 'span',
          },
        },
        styleOverrides: {
          h1: {
            fontSize: "2.75em",
            fontWeight: "bold",
          },
          h2: {
            fontSize: "2em",
            fontWeight: "bold",
          },
          h3: {
            fontSize: "1.25em",
          }
        }
      },
    }
  })

  return (
      <BrowserRouter>
        <CssBaseline/>
        <ThemeProvider theme={theme}>
          <Routes>
            <Route path='/' element={<Layout />} >
              <Route path='/' element={<Frontpage />} />
              <Route path='/profile' element={<Profile />} />
              <Route path='/results/:session' element={<AnnotationResults />} />
              <Route path='/results/:session/view' element={<Editor />} />
              <Route path='/editor/:session' element={<Editor />} />
            </Route>
          </Routes>
        </ThemeProvider>
      </BrowserRouter>

  );
}

export default App;
