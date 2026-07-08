
import tensorflow as tf
from tensorflow.keras import layers, models

def lightweight_unet(input_shape=(256, 256, 3)):
    inputs = layers.Input(input_shape)

    # ENCODER - Ozellik Cikarimi
    c1 = layers.Conv2D(16, (3, 3), activation='relu', padding='same')(inputs)
    p1 = layers.MaxPooling2D((2, 2))(c1)

    c2 = layers.Conv2D(32, (3, 3), activation='relu', padding='same')(p1)
    p2 = layers.MaxPooling2D((2, 2))(c2)

    # BRIDGE - Kopru
    b1 = layers.Conv2D(64, (3, 3), activation='relu', padding='same')(p2)

    # DECODER - Maske Olusturma
    u1 = layers.UpSampling2D((2, 2))(b1)
    m1 = layers.concatenate([u1, c2])
    c3 = layers.Conv2D(32, (3, 3), activation='relu', padding='same')(m1)

    u2 = layers.UpSampling2D((2, 2))(c3)
    m2 = layers.concatenate([u2, c1])
    c4 = layers.Conv2D(16, (3, 3), activation='relu', padding='same')(m2)

    # CIKIS - Hastalik Tahmini
    outputs = layers.Conv2D(1, (1, 1), activation='sigmoid')(c4)

    model = models.Model(inputs=[inputs], outputs=[outputs])
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    
    return model

if __name__ == "__main__":
    unet_model = lightweight_unet()
    unet_model.summary() # Modelin yapisini goster