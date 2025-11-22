import { useState } from 'react';

function InvoiceUpload({ onFileSelect, error }) {
  const [isDragging, setIsDragging] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) {
      handleFileSelect(file);
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      handleFileSelect(file);
    }
  };

  const handleFileSelect = (file) => {
    // Validate file type
    const allowedTypes = ['image/jpeg', 'image/png', 'application/pdf'];
    if (!allowedTypes.includes(file.type)) {
      alert('Invalid file type. Please upload JPG, PNG, or PDF.');
      return;
    }

    // Validate file size (10MB)
    if (file.size > 10 * 1024 * 1024) {
      alert('File size exceeds 10MB limit.');
      return;
    }

    setSelectedFile(file);
    onFileSelect(file);
  };

  return (
    <div className="form-group">
      <label>Upload Invoice *</label>
      <div
        className={`file-upload ${isDragging ? 'dragover' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => document.getElementById('file-input').click()}
      >
        <input
          id="file-input"
          type="file"
          accept="image/jpeg,image/png,application/pdf"
          onChange={handleFileChange}
        />
        {selectedFile ? (
          <div>
            <p>Selected: {selectedFile.name}</p>
            <p style={{ fontSize: '12px', color: '#666' }}>
              {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
            </p>
          </div>
        ) : (
          <div>
            <p>Click to upload or drag and drop</p>
            <p style={{ fontSize: '12px', color: '#666' }}>
              JPG, PNG, or PDF (max 10MB)
            </p>
          </div>
        )}
      </div>
      {error && <div className="error">{error}</div>}
    </div>
  );
}

export default InvoiceUpload;

