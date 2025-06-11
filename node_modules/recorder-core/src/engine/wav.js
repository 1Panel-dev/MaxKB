/*
wav编码器+编码引擎
https://github.com/xiangyuecn/Recorder

当然最佳推荐使用mp3、wav格式，代码也是优先照顾这两种格式
浏览器支持情况
https://developer.mozilla.org/en-US/docs/Web/HTML/Supported_media_formats

编码原理：给pcm数据加上一个44字节的wav头即成wav文件；pcm数据就是Recorder中的buffers原始数据（重新采样），16位时为LE小端模式（Little Endian），实质上是未经过任何编码处理

注意：其他wav编码器可能不是44字节的头，要从任意wav文件中提取pcm数据，请参考：assets/runtime-codes/fragment.decode.wav.js
*/
(function(factory){
	var browser=typeof window=="object" && !!window.document;
	var win=browser?window:Object; //非浏览器环境，Recorder挂载在Object下面
	var rec=win.Recorder,ni=rec.i18n;
	factory(rec,ni,ni.$T,browser);
}(function(Recorder,i18n,$T,isBrowser){
"use strict";

Recorder.prototype.enc_wav={
	stable:true,fast:true
	,getTestMsg:function(){
		return $T("gPSE::支持位数8位、16位（填在比特率里面），采样率取值无限制；此编码器仅在pcm数据前加了一个44字节的wav头，编码出来的16位wav文件去掉开头的44字节即可得到pcm（注：其他wav编码器可能不是44字节）");
	}
};

var NormalizeSet=function(set){
	var bS=set.bitRate,b=bS==8?8:16;
	if(bS!=b) Recorder.CLog($T("wyw9::WAV Info: 不支持{1}位，已更新成{2}位",0,bS,b),3);
	set.bitRate=b;
};

Recorder.prototype.wav=function(res,True,False){
	var This=this,set=This.set;
	
	NormalizeSet(set);
	var size=res.length,sampleRate=set.sampleRate,bitRate=set.bitRate;
	var dataLength=size*(bitRate/8);
	
	//生成wav头
	var header=Recorder.wav_header(1,1,sampleRate,bitRate,dataLength);
	var offset=header.length;
	var bytes=new Uint8Array(offset+dataLength);
	bytes.set(header);
	
	// 写入采样数据
	if(bitRate==8) {
		for(var i=0;i<size;i++) {
			//16转8据说是雷霄骅的 https://blog.csdn.net/sevennight1989/article/details/85376149 细节比blqw的按比例的算法清晰点
			var val=(res[i]>>8)+128;
			bytes[offset++]=val;
		};
	}else{
		bytes=new Int16Array(bytes.buffer);//长度一定是偶数
		bytes.set(res,offset/2);
	};
	
	True(bytes.buffer,"audio/wav");
};

/**
根据参数生成wav文件头，返回Uint8Array（format=1时固定返回44字节，其他返回46字节）
format: 1 (raw pcm) 2 (ADPCM) 3 (IEEE Float) 6 (g711a) 7 (g711u)
numCh: 声道数
dataLength: wav中的音频数据二进制长度
**/
Recorder.wav_header=function(format,numCh,sampleRate,bitRate,dataLength){
	//文件头 http://soundfile.sapp.org/doc/WaveFormat/ https://www.jianshu.com/p/63d7aa88582b https://github.com/mattdiamond/Recorderjs https://www.cnblogs.com/blqw/p/3782420.html https://www.cnblogs.com/xiaoqi/p/6993912.html
	var extSize=format==1?0:2;
	var buffer=new ArrayBuffer(44+extSize);
	var data=new DataView(buffer);
	
	var offset=0;
	var writeString=function(str){
		for (var i=0;i<str.length;i++,offset++) {
			data.setUint8(offset,str.charCodeAt(i));
		};
	};
	var write16=function(v){
		data.setUint16(offset,v,true);
		offset+=2;
	};
	var write32=function(v){
		data.setUint32(offset,v,true);
		offset+=4;
	};
	
	/* RIFF identifier */
	writeString('RIFF');
	/* RIFF chunk length */
	write32(36+extSize+dataLength);
	/* RIFF type */
	writeString('WAVE');
	/* format chunk identifier */
	writeString('fmt ');
	/* format chunk length */
	write32(16+extSize);
	/* audio format */
	write16(format);
	/* channel count */
	write16(numCh);
	/* sample rate */
	write32(sampleRate);
	/* byte rate (sample rate * block align) */
	write32(sampleRate*(numCh*bitRate/8));// *1 声道
	/* block align (channel count * bytes per sample) */
	write16(numCh*bitRate/8);// *1 声道
	/* bits per sample */
	write16(bitRate);
	if(format!=1){// ExtraParamSize 0
		write16(0);
	}
	/* data chunk identifier */
	writeString('data');
	/* data chunk length */
	write32(dataLength);
	
	return new Uint8Array(buffer);
};

}));