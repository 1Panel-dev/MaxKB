/*
录音 Recorder扩展，音频可视化波形显示

https://github.com/xiangyuecn/Recorder

外观和名称来源于：
https://github.com/katspaugh/wavesurfer.js https://github.com/collab-project/videojs-record

本扩展的波形绘制直接简单的使用PCM的采样数值大小来进行线条的绘制，同一段音频绘制出的波形和Audition内显示的波形外观上几乎没有差异。
*/
(function(factory){
	var browser=typeof window=="object" && !!window.document;
	var win=browser?window:Object; //非浏览器环境，Recorder挂载在Object下面
	var rec=win.Recorder,ni=rec.i18n;
	factory(rec,ni,ni.$T,browser);
}(function(Recorder,i18n,$T,isBrowser){
"use strict";

var WaveSurferView=function(set){
	return new fn(set);
};
var ViewTxt="WaveSurferView";
var fn=function(set){
	var This=this;
	var o={
		/*
		elem:"css selector" //自动显示到dom，并以此dom大小为显示大小
			//或者配置显示大小，手动把surferObj.elem显示到别的地方
		,width:0 //显示宽度
		,height:0 //显示高度
		
H5环境以上配置二选一
		
		compatibleCanvas: CanvasObject //提供一个兼容H5的canvas对象，需支持getContext("2d")，支持设置width、height，支持drawImage(canvas,...)
		,compatibleCanvas_2x: CanvasObject //提供一个宽度是compatibleCanvas的2倍canvas对象
		,width:0 //canvas显示宽度
		,height:0 //canvas显示高度
非H5环境使用以上配置
		*/
		
		scale:2 //缩放系数，应为正整数，使用2(3? no!)倍宽高进行绘制，避免移动端绘制模糊
		
		,fps:50 //绘制帧率，不可过高，50-60fps运动性质动画明显会流畅舒适，实际显示帧率达不到这个值也并无太大影响
		
		,duration:2500 //当前视图窗口内最大绘制的波形的持续时间，此处决定了移动速率
		,direction:1 //波形前进方向，取值：1由左往右，-1由右往左
		,position:0 //绘制位置，取值-1到1，-1为最底下，0为中间，1为最顶上，小数为百分比
		
		,centerHeight:1 //中线基础粗细，如果为0不绘制中线，position=±1时应当设为0
		
		//波形颜色配置：[位置，css颜色，...] 位置: 取值0.0-1.0之间
		,linear:[0,"rgba(0,187,17,1)",0.7,"rgba(255,215,0,1)",1,"rgba(255,102,0,1)"]
		,centerColor:"" //中线css颜色，留空取波形第一个渐变颜色
	};
	for(var k in set){
		o[k]=set[k];
	};
	This.set=set=o;
	
	var cCanvas="compatibleCanvas";
	if(set[cCanvas]){
		var canvas=This.canvas=set[cCanvas];
		var canvas2=This.canvas2=set[cCanvas+"_2x"];
	}else{
		if(!isBrowser)throw new Error($T.G("NonBrowser-1",[ViewTxt]));
		var elem=set.elem;
		if(elem){
			if(typeof(elem)=="string"){
				elem=document.querySelector(elem);
			}else if(elem.length){
				elem=elem[0];
			};
		};
		if(elem){
			set.width=elem.offsetWidth;
			set.height=elem.offsetHeight;
		};
		
		var thisElem=This.elem=document.createElement("div");
		thisElem.style.fontSize=0;
		thisElem.innerHTML='<canvas style="width:100%;height:100%;"/>';
		
		var canvas=This.canvas=thisElem.querySelector("canvas");
		var canvas2=This.canvas2=document.createElement("canvas");
		
		if(elem){
			elem.innerHTML="";
			elem.appendChild(thisElem);
		};
	};
	var scale=set.scale;
	var width=set.width*scale;
	var height=set.height*scale;
	if(!width || !height){
		throw new Error($T.G("IllegalArgs-1",[ViewTxt+" width=0 height=0"]));
	};
	
	canvas.width=width;
	canvas.height=height;
	var ctx=This.ctx=canvas.getContext("2d");
	
	canvas2.width=width*2;//卷轴，后台绘制画布能容纳两块窗口内容，进行无缝滚动
	canvas2.height=height;
	var ctx2=This.ctx2=canvas2.getContext("2d");
	
	This.x=0;
};
fn.prototype=WaveSurferView.prototype={
	genLinear:function(ctx,colors,from,to){
		var rtv=ctx.createLinearGradient(0,from,0,to);
		for(var i=0;i<colors.length;){
			rtv.addColorStop(colors[i++],colors[i++]);
		};
		return rtv;
	}
	,input:function(pcmData,powerLevel,sampleRate){
		var This=this;
		This.sampleRate=sampleRate;
		This.pcmData=pcmData;
		This.pcmPos=0;
		
		This.inputTime=Date.now();
		This.schedule();
	}
	,schedule:function(){
		var This=this,set=This.set;
		var interval=Math.floor(1000/set.fps);
		if(!This.timer){
			This.timer=setInterval(function(){
				This.schedule();
			},interval);
		};
		
		var now=Date.now();
		var drawTime=This.drawTime||0;
		if(now-drawTime<interval){
			//没到间隔时间，不绘制
			return;
		};
		This.drawTime=now;
		
		//切分当前需要的绘制数据
		var bufferSize=This.sampleRate/set.fps;
		var pcm=This.pcmData;
		var pos=This.pcmPos;
		var arr=new Int16Array(Math.min(bufferSize,pcm.length-pos));
		for(var i=0;i<arr.length;i++,pos++){
			arr[i]=pcm[pos];
		};
		This.pcmPos=pos;
		
		//推入绘制
		if(arr.length){
			This.draw(arr,This.sampleRate);
		}else{
			if(now-This.inputTime>1300){
				//超时没有输入，干掉定时器
				clearInterval(This.timer);
				This.timer=0;
			};
		};
	}
	,draw:function(pcmData,sampleRate){
		var This=this,set=This.set;
		var ctx=This.ctx2;
		var scale=set.scale;
		var width=set.width*scale;
		var width2=width*2;
		var height=set.height*scale;
		var lineWidth=1*scale;//一条线占用1个单位长度
		
		//计算高度位置
		var position=set.position;
		var posAbs=Math.abs(set.position);
		var originY=position==1?0:height;//y轴原点
		var heightY=height;//最高的一边高度
		if(posAbs<1){
			heightY=heightY/2;
			originY=heightY;
			heightY=Math.floor(heightY*(1+posAbs));
			originY=Math.floor(position>0?originY*(1-posAbs):originY*(1+posAbs));
		};
		
		//计算绘制占用长度
		var pcmDuration=pcmData.length*1000/sampleRate;
		var pcmWidth=pcmDuration*width/set.duration;
		pcmWidth+=This.drawLoss||0;
		var pointCount=0;
		if(pcmWidth<lineWidth){
			This.drawLoss=pcmWidth;
			//pointCount=0; 不够一根不绘制
		}else{
			This.drawLoss=0;
			pointCount=Math.floor(pcmWidth/lineWidth);
		};
		
		//***后台卷轴连续绘制***
		var linear1=This.genLinear(ctx,set.linear,originY,originY-heightY);//上半部分的填充
		var linear2=This.genLinear(ctx,set.linear,originY,originY+heightY);//下半部分的填充
		
		var x=This.x;
		var step=pcmData.length/pointCount;
		for(var i=0,idx=0;i<pointCount;i++){
			var j=Math.floor(idx);
			var end=Math.floor(idx+step);
			idx+=step;
			
			//寻找区间内最大值
			var max=0;
			for(;j<end;j++){
				max=Math.max(max,Math.abs(pcmData[j]));
			};
			
			//计算高度
			var h=heightY*Math.min(1,max/0x7fff);
			
			//绘制当前线条，不管方向，从x:0往x:max方向画就是了
			//绘制上半部分
			if(originY!=0){
				ctx.fillStyle=linear1;
				ctx.fillRect(x, originY-h, lineWidth, h);
			};
			//绘制下半部分
			if(originY!=height){
				ctx.fillStyle=linear2;
				ctx.fillRect(x, originY, lineWidth, h);
			};
			
			x+=lineWidth;
			//超过卷轴宽度，移动画布第二个窗口内容到第一个窗口
			if(x>=width2){
				ctx.clearRect(0,0,width,height);
				ctx.drawImage(This.canvas2,width,0,width,height,0,0,width,height);
				ctx.clearRect(width,0,width,height);
				x=width;
			};
		};
		This.x=x;
		
		//***画回到显示区域***
		ctx=This.ctx;
		ctx.clearRect(0,0,width,height);
		
		//绘制一条中线
		var centerHeight=set.centerHeight*scale;
		if(centerHeight){
			var y=originY-Math.floor(centerHeight/2);
			y=Math.max(y,0);
			y=Math.min(y,height-centerHeight);
			
			ctx.fillStyle=set.centerColor||set.linear[1];
			ctx.fillRect(0, y, width, centerHeight);
		};
		
		//画回画布
		var srcX=0,srcW=x,destX=0;
		if(srcW>width){
			srcX=srcW-width;
			srcW=width;
		}else{
			destX=width-srcW;
		};
		
		var direction=set.direction;
		if(direction==-1){//由右往左
			ctx.drawImage(This.canvas2,srcX,0,srcW,height,destX,0,srcW,height);
		}else{//由左往右
			ctx.save();
			ctx.scale(-1,1);
			ctx.drawImage(This.canvas2,srcX,0,srcW,height,-width+destX,0,srcW,height);
			ctx.restore();
		};
	}
};
Recorder[ViewTxt]=WaveSurferView;

	
}));