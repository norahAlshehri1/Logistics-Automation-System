import { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [file, setFile] = useState(null);
  const [pdfUrl, setPdfUrl] = useState(null);
  const [caseId] = useState(1); 
  const [documentId, setDocumentId] = useState(null); 
  const [extractedData, setExtractedData] = useState({
    "Vendor Name": "",
    "Invoice Number": "",
    "Shipment Date": "",
    "Total Amount": ""
  });
  const [status, setStatus] = useState("Waiting for upload...");

  
  const handleFileUpload = async (e) => {
    e.preventDefault();
    if (!file) return alert("Please select a file first!");

    const formData = new FormData();
    formData.append("file", file);

    try {
      setStatus("Uploading...");
       
      setPdfUrl(URL.createObjectURL(file));

      const uploadRes = await axios.post(`http://127.0.0.1:8000/cases/${caseId}/documents/`, formData);
   
  
      const docId = uploadRes.data.document_id || 1; 
      setDocumentId(docId);
      
      setStatus("Extracting data...");
      handleExtraction(docId);

    } catch (error) {
      setStatus("Error uploading file.");
      console.error(error);
    }
  };

  
  const handleExtraction = async (docId) => {
    try {
      const extractRes = await axios.post(`http://127.0.0.1:8000/documents/${docId}/extract`);
      setExtractedData(extractRes.data.extracted_data);
      setStatus("Data extracted successfully! Please review.");
    } catch (error) {
      setStatus("Error extracting data.");
      console.error(error);
    }
  };

  
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setExtractedData(prev => ({ ...prev, [name]: value }));
  };

  
  const handleApprove = async () => {
    try {
      setStatus("Saving approved data...");
      
      await axios.put(`http://127.0.0.1:8000/documents/${documentId}/approve`, extractedData);
      setStatus("Data Approved and Saved Successfully! ✅");
    } catch (error) {
      setStatus("Error saving data.");
      console.error(error);
    }
  };

  return (
    <div className="app-container">
      <header className="header">
        <h1>Logistics Automation - Review UI</h1>
        <p className="status-bar">Status: <strong>{status}</strong></p>
      </header>

      <div className="main-content">

        <div className="left-pane">
          <h2>1. Document Viewer</h2>
          {!pdfUrl ? (
            <form onSubmit={handleFileUpload} className="upload-form">
              <input type="file" accept="application/pdf" onChange={(e) => setFile(e.target.files[0])} />
              <button type="submit">Upload & Extract</button>
            </form>
          ) : (
            <iframe src={pdfUrl} className="pdf-viewer" title="Invoice PDF"></iframe>
          )}
        </div>

        
        <div className="right-pane">
          <h2>2. Review & Edit Data</h2>
          <div className="form-container">
            {Object.keys(extractedData).map((key) => (
              <div className="form-group" key={key}>
                <label>{key}</label>
                <input
                  type="text"
                  name={key}
                  value={extractedData[key] || ""}
                  onChange={handleInputChange}
                />
              </div>
            ))}
            <button className="approve-btn" onClick={handleApprove} disabled={!documentId}>
              Approve & Save Final Data
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
