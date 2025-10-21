function UCQT_getHexBitmap(canvas) {
  let ctx = canvas.getContext("2d");
  const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
  const pixels = imageData.data;

  const binaryPixels = [];
  for (let i = 0; i < pixels.length; i += 4) {
    const r = pixels[i];
    const g = pixels[i + 1];
    const b = pixels[i + 2];
    const luminance = 0.299 * r + 0.587 * g + 0.114 * b;
    binaryPixels.push(luminance < 128 ? 1 : 0);
  }

  if (canvas.width % 4 !== 0) {
    throw new Error("Canvas is not a multiple of 4 pixels.");
  }

  let hexString = "";
  for (let i = 0; i < binaryPixels.length; i += 4) {
    let val = 0;
    for (let j = 0; j < 4; j++) {
      val |= (binaryPixels[i + j] << (3 - j));
    }
    hexString += val.toString(16);
  }

  return hexString;
}