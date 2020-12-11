from qr_builder import gen_qr_code


def get_qr_image(text):
    return bytes(gen_qr_code(text))
