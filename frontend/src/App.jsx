import { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [file, setFile] = useState(null);
  const [pdfUrl, setPdfUrl] = useState(null);
  const [caseId] = useState(1); // السطر الذي عدلناه سابقاً
  const [documentId, setDocumentId] = useState(null); // <-- هذا هو السطر الذي أضفناه الآن
  const [extractedData, setExtractedData] = useState({
    "Vendor Name": "",
    "Invoice Number": "",
    "Shipment Date": "",
    "Total Amount": ""
  });
  const [status, setStatus] = useState("Waiting for upload...");

  // 1. دالة رفع الملف
  const handleFileUpload = async (e) => {
    e.preventDefault();
    if (!file) return alert("Please select a file first!");

    const formData = new FormData();
    formData.append("file", file);

    try {
      setStatus("Uploading...");
      // إنشاء رابط محلي لعرض الـ PDF في المتصفح مباشرة
      setPdfUrl(URL.createObjectURL(file));

      const uploadRes = await axios.post(`http://127.0.0.1:8000/cases/${caseId}/documents/`, formData);
      // للتبسيط في هذا المثال، نفترض أن الـ API سيعيد رقم المستند
      // يجب أن تعدل الـ Backend ليعيد document_id عند الرفع
      const docId = uploadRes.data.document_id || 1; 
      setDocumentId(docId);
      
      setStatus("Extracting data...");
      handleExtraction(docId);

    } catch (error) {
      setStatus("Error uploading file.");
      console.error(error);
    }
  };

  // 2. دالة جلب البيانات المستخرجة
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

  // 3. دالة التعامل مع تعديلات المستخدم في النموذج
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setExtractedData(prev => ({ ...prev, [name]: value }));
  };

  // 4. دالة الاعتماد والحفظ النهائي
  const handleApprove = async () => {
    try {
      setStatus("Saving approved data...");
      // استدعاء نقطة الاتصال الخاصة بالاعتماد (يجب إضافتها في الخلفية)
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
        {/* النصف الأيسر: عرض المستند */}
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

        {/* النصف الأيمن: نموذج المراجعة والتعديل */}
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