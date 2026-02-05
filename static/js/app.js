// === Estado de la aplicación ===
let selectedFile = null;
let selectedMethod = "opencv";

// === Elementos del DOM ===
const dropZone = document.getElementById("drop-zone");
const fileInput = document.getElementById("file-input");
const previewSection = document.getElementById("preview-section");
const previewImage = document.getElementById("preview-image");
const enhanceBtn = document.getElementById("enhance-btn");
const loading = document.getElementById("loading");
const loadingText = document.getElementById("loading-text");
const resultSection = document.getElementById("result-section");
const uploadSection = document.getElementById("upload-section");
const imgOriginal = document.getElementById("img-original");
const imgEnhanced = document.getElementById("img-enhanced");
const comparisonSlider = document.getElementById("comparison-slider");
const sliderLine = document.getElementById("slider-line");
const imgOriginalOverlay = document.getElementById("img-original-overlay");
const downloadBtn = document.getElementById("download-btn");
const newImageBtn = document.getElementById("new-image-btn");
const methodBtns = document.querySelectorAll(".method-btn");

// === Drag & Drop ===
dropZone.addEventListener("click", () => fileInput.click());

dropZone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropZone.classList.add("dragover");
});

dropZone.addEventListener("dragleave", () => {
    dropZone.classList.remove("dragover");
});

dropZone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropZone.classList.remove("dragover");
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFileSelect(files[0]);
    }
});

fileInput.addEventListener("change", () => {
    if (fileInput.files.length > 0) {
        handleFileSelect(fileInput.files[0]);
    }
});

// === Selección de método ===
methodBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
        methodBtns.forEach((b) => b.classList.remove("active"));
        btn.classList.add("active");
        selectedMethod = btn.dataset.method;
    });
});

// === Manejo de archivo seleccionado ===
function handleFileSelect(file) {
    if (!file.type.startsWith("image/")) {
        alert("Por favor seleccioná un archivo de imagen.");
        return;
    }

    if (file.size > 16 * 1024 * 1024) {
        alert("La imagen es demasiado grande. El máximo es 16 MB.");
        return;
    }

    selectedFile = file;

    // Mostrar preview
    const reader = new FileReader();
    reader.onload = (e) => {
        previewImage.src = e.target.result;
        previewSection.classList.remove("hidden");
    };
    reader.readAsDataURL(file);
}

// === Enviar imagen al servidor ===
enhanceBtn.addEventListener("click", async () => {
    if (!selectedFile) return;

    // Mostrar loading, ocultar otros
    uploadSection.classList.add("hidden");
    resultSection.classList.add("hidden");
    loading.classList.remove("hidden");

    if (selectedMethod === "waternet") {
        loadingText.textContent = "Procesando con WaterNet (IA)... Esto puede tardar unos segundos.";
    } else {
        loadingText.textContent = "Procesando con OpenCV...";
    }

    const formData = new FormData();
    formData.append("file", selectedFile);
    formData.append("method", selectedMethod);

    try {
        const response = await fetch("/upload", {
            method: "POST",
            body: formData,
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Error al procesar la imagen");
        }

        showResult(data.original, data.enhanced);
    } catch (err) {
        alert("Error: " + err.message);
        uploadSection.classList.remove("hidden");
    } finally {
        loading.classList.add("hidden");
    }
});

// === Mostrar resultado con slider ===
function showResult(originalUrl, enhancedUrl) {
    // Agregar timestamp para evitar cache
    const ts = "?t=" + Date.now();
    imgOriginal.src = originalUrl + ts;
    imgEnhanced.src = enhancedUrl + ts;

    // Configurar el tamaño del overlay de la imagen original
    imgEnhanced.onload = () => {
        const w = imgEnhanced.naturalWidth;
        const h = imgEnhanced.naturalHeight;
        imgOriginal.style.width = imgEnhanced.offsetWidth + "px";
        imgOriginal.style.height = imgEnhanced.offsetHeight + "px";

        // Resetear slider al 50%
        comparisonSlider.value = 50;
        updateSlider(50);
    };

    downloadBtn.href = enhancedUrl;

    resultSection.classList.remove("hidden");
}

// === Control del slider ===
comparisonSlider.addEventListener("input", (e) => {
    updateSlider(e.target.value);
});

function updateSlider(value) {
    const percent = value + "%";
    imgOriginalOverlay.style.width = percent;
    sliderLine.style.left = percent;
}

// === Procesar otra imagen ===
newImageBtn.addEventListener("click", () => {
    resultSection.classList.add("hidden");
    previewSection.classList.add("hidden");
    uploadSection.classList.remove("hidden");
    selectedFile = null;
    fileInput.value = "";
});

// === Resize handler para mantener proporciones del slider ===
window.addEventListener("resize", () => {
    if (!resultSection.classList.contains("hidden")) {
        imgOriginal.style.width = imgEnhanced.offsetWidth + "px";
        imgOriginal.style.height = imgEnhanced.offsetHeight + "px";
    }
});
