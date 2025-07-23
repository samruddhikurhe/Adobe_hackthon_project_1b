import os
from optimum.onnxruntime import ORTQuantizer, ORTModelForFeatureExtraction
from optimum.onnxruntime.configuration import AutoQuantizationConfig

# Define the paths for the original, intermediate, and final models.
MODEL_PATH = 'models/msmarco-distilbert-base-v2'
ONNX_PATH = 'models/msmarco-distilbert-base-v2-onnx'
QUANTIZED_PATH = 'models/msmarco-distilbert-base-v2-quantized'

def quantize_model():
    """
    Exports a Sentence Transformer model to ONNX format and then applies
    dynamic quantization for CPU execution.
    """
    print(f"Loading base model from: {MODEL_PATH}")

    # Step 1: Export the base model to ONNX format.
    # This is a prerequisite for quantization with the Optimum library.
    if not os.path.exists(ONNX_PATH):
        print(f"Exporting model to ONNX format at: {ONNX_PATH}...")
        # ORTModelForFeatureExtraction handles the conversion from a transformers
        # model to an ONNX-compatible model.
        model = ORTModelForFeatureExtraction.from_pretrained(MODEL_PATH, export=True)
        model.save_pretrained(ONNX_PATH)
        print("ONNX export complete.")
    else:
        print(f"ONNX model already exists at {ONNX_PATH}. Skipping export.")

    # Step 2: Create a quantizer for the newly created ONNX model.
    print(f"Loading ONNX model from {ONNX_PATH} for quantization...")
    quantizer = ORTQuantizer.from_pretrained(ONNX_PATH)

    # Step 3: Define the dynamic quantization configuration for CPU (AVX2).
    # This creates a proper configuration object, which is the correct
    # way to specify quantization settings.
    dqconfig = AutoQuantizationConfig.avx2(is_static=False, use_symmetric_activations=False)

    # Step 4: Apply quantization to the model.
    print(f"Quantizing model and saving to: {QUANTIZED_PATH}...")
    # The quantize method takes the save directory and the configuration object.
    quantizer.quantize(
        save_dir=QUANTIZED_PATH,
        quantization_config=dqconfig
    )
    print(f"Quantized model saved successfully to: {QUANTIZED_PATH}")

if __name__ == "__main__":
    quantize_model()
