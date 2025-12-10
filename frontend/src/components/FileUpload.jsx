import { useRef, useState } from "react";
import { Upload, File, X } from "lucide-react";

const FileUpload = ({
  accept,
  onFileSelect,
  label = "Upload file",
  subLabel = "Drag and drop or click",
}) => {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const inputRef = useRef(null);

  const handleDrag = (event) => {
    event.preventDefault();
    event.stopPropagation();
    if (event.type === "dragenter" || event.type === "dragover") {
      setDragActive(true);
    } else if (event.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (event) => {
    event.preventDefault();
    event.stopPropagation();
    setDragActive(false);
    if (event.dataTransfer.files && event.dataTransfer.files[0]) {
      handleFile(event.dataTransfer.files[0]);
    }
  };

  const handleChange = (event) => {
    event.preventDefault();
    if (event.target.files && event.target.files[0]) {
      handleFile(event.target.files[0]);
    }
  };

  const handleFile = (file) => {
    setSelectedFile(file);
    onFileSelect(file);
  };

  const clearFile = (event) => {
    event.stopPropagation();
    setSelectedFile(null);
    if (inputRef.current) {
      inputRef.current.value = "";
    }
  };

  return (
    <div className="w-full font-mono text-sm">
      <div
        className={`group relative w-full border border-dashed p-8 transition-all duration-200 text-center cursor-pointer bg-black ${
          dragActive
            ? "border-white bg-zinc-900"
            : "border-zinc-800 hover:border-zinc-600 hover:bg-zinc-900/30"
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
      >
        <input
          ref={inputRef}
          type="file"
          className="hidden"
          accept={accept}
          onChange={handleChange}
        />

        {selectedFile ? (
          <div className="flex items-center justify-between p-2 bg-zinc-900 border border-zinc-800">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 flex items-center justify-center bg-zinc-800 text-zinc-300">
                <File className="w-4 h-4" />
              </div>
              <div className="text-left">
                <p className="text-white font-medium truncate max-w-[200px]">
                  {selectedFile.name}
                </p>
                <p className="text-xs text-zinc-500">
                  {(selectedFile.size / 1024).toFixed(2)} KB
                </p>
              </div>
            </div>

            <button
              onClick={clearFile}
              className="p-2 hover:bg-zinc-800 text-zinc-500 hover:text-white transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        ) : (
          <div className="flex flex-col items-center py-6">
            <div
              className={`mb-4 transition-colors ${
                dragActive
                  ? "text-white"
                  : "text-zinc-600 group-hover:text-zinc-400"
              }`}
            >
              <Upload className="w-6 h-6" />
            </div>
            <p className="text-zinc-300 font-medium mb-1">{label}</p>
            <p className="text-xs text-zinc-600 uppercase tracking-wide">
              {subLabel}
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default FileUpload;

