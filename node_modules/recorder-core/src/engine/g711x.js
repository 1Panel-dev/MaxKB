/*
g711x编码器+解码器
https://github.com/xiangyuecn/Recorder

可用type：
	g711a: G.711 A-law (pcma)
	g711u: G.711 μ-law (pcmu、mu-law)

编解码源码移植自：https://github.com/twstx1/codec-for-audio-in-G72X-G711-G723-G726-G729/blob/master/G711_G721_G723/g711.c
移植相关测试代码（FFmpeg转码、播放命令）：assets/runtime-codes/test.g7xx.engine.js
*/
(function(factory){
	var browser=typeof window=="object" && !!window.document;
	var win=browser?window:Object; //非浏览器环境，Recorder挂载在Object下面
	var rec=win.Recorder,ni=rec.i18n;
	factory(rec,ni,ni.$T,browser);
}(function(Recorder,i18n,$T,isBrowser){
"use strict";

var regEngine=function(key,desc,enc,dec){

Recorder.prototype["enc_"+key]={
	stable:true,fast:true
	,getTestMsg:function(){
		return $T("d8YX::{1}；{2}音频文件无法直接播放，可用Recorder.{2}2wav()转码成wav播放；采样率比特率设置无效，固定为8000hz采样率、16位，每个采样压缩成8位存储，音频文件大小为8000字节/秒；如需任意采样率支持，请使用Recorder.{2}_encode()方法",0,desc,key);
	}
};

//*******标准UI线程转码支持函数************
Recorder.prototype[key]=function(res,True,False){
	var This=this,set=This.set,srcSampleRate=set.sampleRate,sampleRate=8000;
	set.bitRate=16;
	set.sampleRate=sampleRate;
	if(srcSampleRate>sampleRate){
		res=Recorder.SampleData([res],srcSampleRate,sampleRate).data;
	}else if(srcSampleRate<sampleRate){
		False($T("29UK::数据采样率低于{1}",0,sampleRate)); return;
	};
	var bytes=enc(res);
	True(bytes.buffer,"audio/"+key);
};

/**编码任意采样率的pcm得到g711x数据
pcm: Int16Array，任意采样率pcm数据（标准采样率为8000）
返回Uint8Array，g711x二进制数据（采样率为pcm的采样率）
**/
Recorder[key+"_encode"]=function(pcm){
	return enc(pcm);
};
/**解码g711x得到pcm
bytes: Uint8Array，g711x二进制数据，采样率一般是8000
返回Int16Array，为g711x的采样率、16位的pcm数据
**/
Recorder[key+"_decode"]=function(bytes){
	return dec(bytes);
};

/**g711x直接转码成wav，可以直接用来播放；需同时引入src/engine/wav.js
g711xBlob: g711x音频文件blob对象 或 ArrayBuffer（回调也将返回ArrayBuffer），采样率只支持8000
True(wavBlob,duration,mime)
False(msg)
**/
Recorder[key+"2wav"]=function(g711xBlob,True,False){
	if(!Recorder.prototype.wav){
		False($T.G("NeedImport-2",[key+"2wav","src/engine/wav.js"]));
		return;
	};
	
	var loadOk=function(arrB,dArrB){
		var bytes=new Uint8Array(arrB);
		var pcm=dec(bytes);
		
		var rec=Recorder({
			type:"wav",sampleRate:8000,bitRate:16
		});
		if(dArrB)rec.dataType="arraybuffer";
		rec.mock(pcm,8000).stop(function(wavBlob,duration,mime){
			True(wavBlob,duration,mime);
		},False);
	};
	
	if(g711xBlob instanceof ArrayBuffer){
		loadOk(g711xBlob,1);
	}else{
		var reader=new FileReader();
		reader.onloadend=function(){
			loadOk(reader.result);
		};
		reader.readAsArrayBuffer(g711xBlob);
	};
};




//********边录边转码支持函数，g711转码超快，因此也是工作在UI线程（非Worker）*********
Recorder.prototype[key+"_envCheck"]=function(envInfo,set){//检查环境下配置是否可用
	return ""; //没有需要检查的内容
};

Recorder.prototype[key+"_start"]=function(set){//如果返回null代表不支持
	set.bitRate=16;
	set.sampleRate=8000;
	return {set:set, memory:new Uint8Array(500000), mOffset:0};
};
var addBytes=function(cur,buf){
	var bufLen=buf.length;
	if(cur.mOffset+bufLen>cur.memory.length){
		var tmp=new Uint8Array(cur.memory.length+Math.max(500000,bufLen));
		tmp.set(cur.memory.subarray(0, cur.mOffset));
		cur.memory=tmp;
	}
	cur.memory.set(buf,cur.mOffset);
	cur.mOffset+=bufLen;
};

Recorder.prototype[key+"_stop"]=function(startCtx){
	if(startCtx&&startCtx.memory){
		startCtx.memory=null;
	}
};
Recorder.prototype[key+"_encode"]=function(startCtx,pcm){
	if(startCtx&&startCtx.memory){
		var set=startCtx.set;
		var bytes=enc(pcm);
		
		if(set.takeoffEncodeChunk){
			set.takeoffEncodeChunk(bytes);
		}else{
			addBytes(startCtx, bytes);
		};
	};
};
Recorder.prototype[key+"_complete"]=function(startCtx,True,False,autoStop){
	if(startCtx&&startCtx.memory){
		if(autoStop){
			this[key+"_stop"](startCtx);
		};
		var buffer=startCtx.memory.buffer.slice(0,startCtx.mOffset);
		True(buffer,"audio/"+key);
	}else{
		False($T("quVJ::{1}编码器未start",0,key));
	};
};

};



var Tab=[1,2,3,3,4,4,4,4,5,5,5,5,5,5,5,5,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7];

regEngine("g711a","G.711 A-law (pcma)"
,function(pcm){//编码
	var buffer=new Uint8Array(pcm.length);
	for(var i=0;i<pcm.length;i++){
		var pcm_val=pcm[i],mask;

		if (pcm_val >= 0) {
			mask = 0xD5;		/* sign (7th) bit = 1 */
		} else {
			mask = 0x55;		/* sign bit = 0 */
			pcm_val = -pcm_val - 1;
		}

		/* Convert the scaled magnitude to segment number. */
		var seg = (Tab[pcm_val>>8&0x7F]||8)-1;
		
		/* Combine the sign, segment, and quantization bits. */
		var aval = seg << 4;
		if (seg < 2)
			aval |= (pcm_val >> 4) & 15;
		else
			aval |= (pcm_val >> (seg + 3)) & 15;
		buffer[i] = (aval ^ mask);
	}
	return buffer;
}
,function(bytes){//解码
	var buffer=new Int16Array(bytes.length);
	for(var i=0;i<bytes.length;i++){
		var a_val=bytes[i]^0x55;
		var t = (a_val & 15) << 4;
		var seg = (a_val & 0x70) >> 4;
		switch (seg) {
		case 0:
			t += 8; break;
		case 1:
			t += 0x108; break;
		default:
			t += 0x108;
			t <<= seg - 1;
		}
		buffer[i] = ((a_val & 0x80) ? t : -t);
	}
	return buffer;
});


regEngine("g711u","G.711 μ-law (pcmu、mu-law)"
,function(pcm){//编码
	var buffer=new Uint8Array(pcm.length);
	for(var i=0;i<pcm.length;i++){
		var pcm_val=pcm[i],mask;
		
		/* Get the sign and the magnitude of the value. */
		if (pcm_val < 0) {
			pcm_val = 0x84 - pcm_val;
			mask = 0x7F;
		} else {
			pcm_val += 0x84;
			mask = 0xFF;
		}
		
		/* Convert the scaled magnitude to segment number. */
		var seg = (Tab[pcm_val>>8&0x7F]||8)-1;
		
		var uval = (seg << 4) | ((pcm_val >> (seg + 3)) & 0xF);
		buffer[i] = (uval ^ mask);
	}
	return buffer;
}
,function(bytes){//解码
	var buffer=new Int16Array(bytes.length);
	for(var i=0;i<bytes.length;i++){
		var u_val= ~bytes[i];
		
		var t = ((u_val & 15) << 3) + 0x84;
		t <<= (u_val & 0x70) >> 4;

		buffer[i] = ((u_val & 0x80) ? (0x84 - t) : (t - 0x84));
	}
	return buffer;
});


}));