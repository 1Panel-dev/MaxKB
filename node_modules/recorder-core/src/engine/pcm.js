/*
pcm编码器+编码引擎
https://github.com/xiangyuecn/Recorder

编码原理：本编码器输出的pcm格式数据其实就是Recorder中的buffers原始数据（经过了重新采样），16位时为LE小端模式（Little Endian），并未经过任何编码处理

编码的代码和wav.js区别不大，pcm加上一个44字节wav头即成wav文件；所以要播放pcm就很简单了，直接转成wav文件来播放，已提供转换函数 Recorder.pcm2wav
*/
(function(factory){
	var browser=typeof window=="object" && !!window.document;
	var win=browser?window:Object; //非浏览器环境，Recorder挂载在Object下面
	var rec=win.Recorder,ni=rec.i18n;
	factory(rec,ni,ni.$T,browser);
}(function(Recorder,i18n,$T,isBrowser){
"use strict";

Recorder.prototype.enc_pcm={
	stable:true,fast:true
	,getTestMsg:function(){
		return $T("fWsN::pcm为未封装的原始音频数据，pcm音频文件无法直接播放，可用Recorder.pcm2wav()转码成wav播放；支持位数8位、16位（填在比特率里面），采样率取值无限制");
	}
};

var NormalizeSet=function(set){
	var bS=set.bitRate,b=bS==8?8:16;
	if(bS!=b) Recorder.CLog($T("uMUJ::PCM Info: 不支持{1}位，已更新成{2}位",0,bS,b),3);
	set.bitRate=b;
};



//*******标准UI线程转码支持函数************

Recorder.prototype.pcm=function(res,True,False){
	var set=this.set;
	NormalizeSet(set);
	var bytes=PcmEncode(res,set.bitRate);
	True(bytes.buffer,"audio/pcm");
};

var PcmEncode=function(pcm,bitRate){
	if(bitRate==8) {
		var size=pcm.length;
		var bytes=new Uint8Array(size);
		for(var i=0;i<size;i++){
			//16转8据说是雷霄骅的 https://blog.csdn.net/sevennight1989/article/details/85376149 细节比blqw的按比例的算法清晰点
			var val=(pcm[i]>>8)+128;
			bytes[i]=val;
		};
	}else{
		pcm=new Int16Array(pcm); //复制一份
		var bytes=new Uint8Array(pcm.buffer);
	};
	return bytes;
};





/**pcm直接转码成wav，可以直接用来播放；需同时引入src/engine/wav.js
data: {
		sampleRate:16000 pcm的采样率
		bitRate:16 pcm的位数 取值：8 或 16
		blob:blob对象 或 ArrayBuffer（回调也将返回ArrayBuffer）
	}
	data如果直接提供的blob将默认使用16位16khz的配置，仅用于测试
True(wavBlob,duration,mime)
False(msg)
**/
Recorder.pcm2wav=function(data,True,False){
	if(!data.blob){//Blob 测试用
		data={blob:data};
	};
	var blob=data.blob;
	var sampleRate=data.sampleRate||16000,bitRate=data.bitRate||16;
	if(!data.sampleRate || !data.bitRate){
		Recorder.CLog($T("KmRz::pcm2wav必须提供sampleRate和bitRate"),3);
	};
	if(!Recorder.prototype.wav){
		False($T.G("NeedImport-2",["pcm2wav","src/engine/wav.js"]));
		return;
	};
	
	var loadOk=function(arrB,dArrB){
		var pcm;
		if(bitRate==8){
			//8位转成16位
			var u8arr=new Uint8Array(arrB);
			pcm=new Int16Array(u8arr.length);
			for(var j=0;j<u8arr.length;j++){
				pcm[j]=(u8arr[j]-128)<<8;
			};
		}else{
			pcm=new Int16Array(arrB);
		};
		
		var rec=Recorder({
			type:"wav"
			,sampleRate:sampleRate
			,bitRate:bitRate
		});
		if(dArrB)rec.dataType="arraybuffer";
		rec.mock(pcm,sampleRate).stop(function(wavBlob,duration,mime){
			True(wavBlob,duration,mime);
		},False);
	};
	
	if(blob instanceof ArrayBuffer){
		loadOk(blob,1);
	}else{
		var reader=new FileReader();
		reader.onloadend=function(){
			loadOk(reader.result);
		};
		reader.readAsArrayBuffer(blob);
	};
};



//********边录边转码支持函数，pcm转码超快，因此也是工作在UI线程（非Worker）*********
Recorder.prototype.pcm_envCheck=function(envInfo,set){//检查环境下配置是否可用
	return ""; //没有需要检查的内容
};

Recorder.prototype.pcm_start=function(set){//如果返回null代表不支持
	NormalizeSet(set);
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

Recorder.prototype.pcm_stop=function(startCtx){
	if(startCtx&&startCtx.memory){
		startCtx.memory=null;
	}
};
Recorder.prototype.pcm_encode=function(startCtx,pcm){
	if(startCtx&&startCtx.memory){
		var set=startCtx.set;
		var bytes=PcmEncode(pcm, set.bitRate);
		
		if(set.takeoffEncodeChunk){
			set.takeoffEncodeChunk(bytes);
		}else{
			addBytes(startCtx, bytes);
		};
	};
};
Recorder.prototype.pcm_complete=function(startCtx,True,False,autoStop){
	if(startCtx&&startCtx.memory){
		if(autoStop){
			this.pcm_stop(startCtx);
		};
		var buffer=startCtx.memory.buffer.slice(0,startCtx.mOffset);
		True(buffer,"audio/pcm");
	}else{
		False($T("sDkA::pcm编码器未start"));
	};
};




}));