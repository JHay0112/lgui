/**
 * Run upon load of lgui
 * Loads in canvas and 
 */

const CANVAS_ID = "canvas";

/**
 * Gets the canvas from the document
 */
function getCanvas() {
    let canvas = document.getElementById(CANVAS_ID);
    canvas.width = window.screen.width;
    canvas.height = window.screen.height;
    return canvas;
}

/**
 * Draws the grid that components fall on
 */
function drawGrid() {
    const DOT_RADIUS = 1;
    const DOT_SPACING = 24;

    let canvas = getCanvas();
    let context = canvas.getContext("2d");

    let nxDots = Math.floor(canvas.width / (DOT_RADIUS + DOT_SPACING));
    let nyDots = Math.floor(canvas.height / (DOT_RADIUS + DOT_SPACING));

    for (i = 0; i < nxDots; i++) {
        for (j = 0; j < nyDots; j++) {
            context.beginPath();
            context.arc(
                i * (DOT_SPACING + DOT_RADIUS/2) + DOT_SPACING, 
                j * (DOT_SPACING + DOT_RADIUS/2) + DOT_SPACING, DOT_RADIUS, 
                0, 2*Math.PI
            );
            context.fillStyle = "black";
            context.fill();
        }
    }
}

/**
 * Runs the following upon load
 */
function onLoad() {
    drawGrid();
}