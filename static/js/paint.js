var canvas = document.getElementById("paint");
var ctx = canvas.getContext("2d");

var sketch = document.querySelector('#sketch');
var sketch_style = getComputedStyle(sketch);
canvas.width = parseInt(sketch_style.getPropertyValue('width'));
canvas.height = parseInt(sketch_style.getPropertyValue('height'));

var width = canvas.width, height = canvas.height;
var curX, curY, prevX, prevY;
var hold = false;
var fill_value = true, stroke_value = false;
var canvas_data = { "pencil": [], "line": [], "rectangle": [], "circle": [], "eraser": [] };
ctx.fillStyle = 'white';

function pencil(){
	
    ctx.lineWidth = 5;
    ctx.strokeStyle = 'black';
        
    canvas.onmousedown = function (e){
        curX = e.pageX - canvas.offsetLeft;
        curY = e.pageY - canvas.offsetTop;
        hold = true;
            
        prevX = curX;
        prevY = curY;
        ctx.beginPath();
        ctx.moveTo(prevX, prevY);
    };
        
    canvas.onmousemove = function (e){
        if(hold){
            curX = e.pageX - canvas.offsetLeft;
            curY = e.pageY - canvas.offsetTop;
            draw();
        }
    };
        
    canvas.onmouseup = function (e){
        hold = false;
    };
        
    canvas.onmouseout = function (e){
        hold = false;
    };
        
    function draw (){
        ctx.lineTo(curX, curY);
        ctx.stroke();
        canvas_data.pencil.push({ "startx": prevX, "starty": prevY, "endx": curX, "endy": curY,
            "thick": ctx.lineWidth, "color": ctx.strokeStyle });
    }
}
function line (){
           
    ctx.lineWidth = 5;
    ctx.strokeStyle = 'black';

    canvas.onmousedown = function (e){
        img = ctx.getImageData(0, 0, width, height);
        prevX = e.pageX - canvas.offsetLeft;
        prevY = e.pageY - canvas.offsetTop;
        hold = true;
    };
            
    canvas.onmousemove = function (e){
        if (hold){
            ctx.putImageData(img, 0, 0);
            curX = e.pageX - canvas.offsetLeft;
            curY = e.pageY - canvas.offsetTop;
            ctx.beginPath();
            ctx.moveTo(prevX, prevY);
            ctx.lineTo(curX, curY);
            ctx.stroke();
            canvas_data.line.push({ "starx": prevX, "starty": prevY, "endx": curX, "endY": curY,
                 "thick": ctx.lineWidth, "color": ctx.strokeStyle });
            ctx.closePath();
        }
    };
            
    canvas.onmouseup = function (e){
         hold = false;
    };
            
    canvas.onmouseout = function (e){
         hold = false;
    };
}
function rectangle (){
            
    ctx.lineWidth = 5;
    ctx.strokeStyle = 'black';

    canvas.onmousedown = function (e){
        img = ctx.getImageData(0, 0, width, height);
        prevX = e.pageX - canvas.offsetLeft;
        prevY = e.pageY - canvas.offsetTop;
        hold = true;
    };
            
    canvas.onmousemove = function (e){
        if (hold){
            ctx.putImageData(img, 0, 0);
            curX = e.pageX - canvas.offsetLeft - prevX;
            curY = e.pageY - canvas.offsetTop - prevY;
            ctx.strokeRect(prevX, prevY, curX, curY);
            if (fill_value){
                ctx.fillRect(prevX, prevY, curX, curY);
            }
            canvas_data.rectangle.push({ "starx": prevX, "stary": prevY, "width": curX, "height": curY,
                "thick": ctx.lineWidth, "stroke": stroke_value, "stroke_color": ctx.strokeStyle, "fill": fill_value,
                "fill_color": ctx.fillStyle });
            
        }
    };
            
    canvas.onmouseup = function (e){
        hold = false;
    };
            
    canvas.onmouseout = function (e){
        hold = false;
    };
}

function circle (){
        
    ctx.lineWidth = 5;
    ctx.strokeStyle = 'black';
    
    canvas.onmousedown = function (e){
        img = ctx.getImageData(0, 0, width, height);
        prevX = e.pageX - canvas.offsetLeft;
        prevY = e.pageY - canvas.offsetTop;
        hold = true;
    };
            
    canvas.onmousemove = function (e){
        if (hold){
            ctx.putImageData(img, 0, 0);
            curX = e.pageX - canvas.offsetLeft;
            curY = e.pageY - canvas.offsetTop;
            ctx.beginPath();
            ctx.arc(Math.abs(curX + prevX)/2, Math.abs(curY + prevY)/2,
                Math.sqrt(Math.pow(curX - prevX, 2) + Math.pow(curY - prevY, 2))/2, 0, Math.PI * 2, true);
            ctx.closePath();
            ctx.stroke();
            if (fill_value)
                ctx.fill();
            canvas_data.circle.push({ "starx": prevX, "stary": prevY, "radius": curX - prevX, "thick": ctx.lineWidth,
                "stroke": stroke_value, "stroke_color": ctx.strokeStyle, "fill": fill_value, "fill_color": ctx.fillStyle });
        }
    };
            
    canvas.onmouseup = function (e){
        hold = false;
    };
            
    canvas.onmouseout = function (e){
        hold = false;
    };
}

function eraser (){

    ctx.lineStyle = 8;

    canvas.onmousedown = function (e){
        curX = e.pageX - canvas.offsetLeft;
        curY = e.pageY - canvas.offsetTop;
        hold = true;
            
        prevX = curX;
        prevY = curY;
        ctx.beginPath();
        ctx.moveTo(prevX, prevY);
    };
        
    canvas.onmousemove = function (e){
        if(hold){
            curX = e.pageX - canvas.offsetLeft;
            curY = e.pageY - canvas.offsetTop;
            draw();
        }
    };
        
    canvas.onmouseup = function (e){
        hold = false;
    };
        
    canvas.onmouseout = function (e){
        hold = false;
    };
        
    function draw (){
        ctx.lineTo(curX, curY);
        ctx.strokeStyle = "#ffffff";
        ctx.stroke();
        canvas_data.eraser.push({ "startx": prevX, "starty": prevY, "endx": curX, "endy": curY,
            "thick": ctx.lineWidth, "color": ctx.strokeStyle });
    }
}
