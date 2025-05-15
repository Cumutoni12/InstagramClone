import Header from "./components/header";
import Footer from "./components/Footer";
import "./App.css";
import "./components/header.css"; // Header specific styles
import "./components/Footer.css"; // Footer specific styles

function App() {
  return (
    <div className="app--container">
      <Header />
      <main className="app-main container">
        {/*content of the current page will go here */}
        <h2>Welcome to the Instagram Clone</h2>
        <p>Start by creating or logging into an account. </p>
      </main>
      <Footer />
    </div>
  );
}

export default App;
