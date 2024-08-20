from PIL import Image, ImageFile
import os

# Ensure PIL can handle truncated images
ImageFile.LOAD_TRUNCATED_IMAGES = True

def reducir_tamano_imagen(input_path, output_path, max_size):
    try:
        # Abre la imagen
        with Image.open(input_path) as img:
            # Calcula la proporción de la reducción
            ratio = min(max_size/img.size[0], max_size/img.size[1])
            
            # Calcula el nuevo tamaño
            new_size = (int(img.size[0]*ratio), int(img.size[1]*ratio))
            
            # Redimensiona la imagen
            img = img.resize(new_size, Image.LANCZOS)
            
            # Si la imagen tiene un canal alfa, conviértela a RGB
            if img.mode == 'RGBA':
                img = img.convert('RGB')
            
            # Guarda la imagen redimensionada
            img.save(output_path, optimize=True, quality=85)
            print(f"Processed {input_path} successfully")
    except Exception as e:
        print(f"Failed to process {input_path}: {e}")

# Tamaño máximo (en píxeles) del lado más largo
max_size = 800

# Directorio de imágenes de entrada
input_dir = "./Fotos/Termicas"

# Directorio donde se guardarán las imágenes reducidas
output_dir = "./Fotos/Termicas Reporte"

# Crear el directorio de salida si no existe
os.makedirs(output_dir, exist_ok=True)

for filename in os.listdir(input_dir):
    if filename.endswith(('.jpg', '.jpeg', '.png', '.JPG')):
        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, filename)
        reducir_tamano_imagen(input_path, output_path, max_size)

print("All images processed.")
