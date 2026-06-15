import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { motion } from 'framer-motion';
import { FiUploadCloud, FiImage } from 'react-icons/fi';

const ImageUpload = ({ onFileSelect }) => {
    const onDrop = useCallback((acceptedFiles) => {
        if (acceptedFiles?.length > 0) {
            const file = acceptedFiles[0];
            // Create preview
            const previewUrl = URL.createObjectURL(file);
            onFileSelect(file, previewUrl);
        }
    }, [onFileSelect]);

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: { 'image/*': [] },
        multiple: false
    });

    return (
        <motion.div
            {...getRootProps()}
            whileHover={{ scale: 1.02, borderColor: '#00f2ff' }}
            whileTap={{ scale: 0.98 }}
            style={{
                border: '2px dashed #1a2138',
                borderRadius: '16px',
                padding: '3rem',
                textAlign: 'center',
                cursor: 'pointer',
                background: isDragActive ? 'rgba(0, 242, 255, 0.1)' : 'rgba(10, 14, 23, 0.5)',
                transition: 'all 0.3s ease'
            }}
        >
            <input {...getInputProps()} />
            <div style={{ marginBottom: '1rem', color: '#00f2ff', fontSize: '3rem' }}>
                {isDragActive ? <FiImage /> : <FiUploadCloud />}
            </div>
            <h3 style={{ color: '#e0e6ed', marginBottom: '0.5rem' }}>
                {isDragActive ? "Drop image here..." : "Drag & Drop Image"}
            </h3>
            <p style={{ color: '#94a3b8', fontSize: '0.9rem' }}>
                Supports JPG, PNG, WEBP (Max 10MB)
            </p>
        </motion.div>
    );
};

export default ImageUpload;
