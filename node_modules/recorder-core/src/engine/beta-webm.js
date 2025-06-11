/*
webm编码器，beta版
https://github.com/xiangyuecn/Recorder

当然最佳推荐使用mp3、wav格式，代码也是优先照顾这两种格式
浏览器支持情况
https://developer.mozilla.org/en-US/docs/Web/HTML/Supported_media_formats
*/
(function(factory){
	var browser=typeof window=="object" && !!window.document;
	var win=browser?window:Object; //非浏览器环境，Recorder挂载在Object下面
	var rec=win.Recorder,ni=rec.i18n;
	factory(rec,ni,ni.$T,browser);
}(function(Recorder,i18n,$T,isBrowser){
"use strict";

var mime="audio/webm";
var support=isBrowser&&window.MediaRecorder&&MediaRecorder.isTypeSupported(mime);


Recorder.prototype.enc_webm={
	stable:false
	,getTestMsg:function(){
		if(!support) return $T("L49q::此浏览器不支持进行webm编码，未实现MediaRecorder");
		return $T("tsTW::只有比较新的浏览器支持，压缩率和mp3差不多。由于未找到对已有pcm数据进行快速编码的方法，只能按照类似边播放边收听形式把数据导入到MediaRecorder，有几秒就要等几秒。输出音频虽然可以通过比特率来控制文件大小，但音频文件中的比特率并非设定比特率，采样率由于是我们自己采样的，到这个编码器随他怎么搞");
	}
};
Recorder.prototype.webm=function(res,True,False){
		//https://developer.mozilla.org/en-US/docs/Web/API/MediaRecorder/MediaRecorder
		//https://developer.mozilla.org/en-US/docs/Web/API/MediaStreamAudioDestinationNode
		if(!isBrowser){
			False($T.G("NonBrowser-1",["webm encoder"]));
			return;
		};
		if(!support){
			False($T("aG4z::此浏览器不支持把录音转成webm格式"));
			return;
		};
		var This=this, set=This.set,size=res.length,sampleRate=set.sampleRate;
		
		var ctx=Recorder.GetContext(true);
		var endCall=function(){
			Recorder.CloseNewCtx(ctx);
		};
		
		var dest=ctx.createMediaStreamDestination();
		dest.channelCount=1;
		
		//录音啦
		var recorder = new MediaRecorder(dest.stream,{
			mimeType:mime
			,bitsPerSecond:set.bitRate*1000
		});
		var chunks = [];
		recorder.ondataavailable=function(e) {
			chunks.push(e.data);
		};
		recorder.onstop=function(e) {
			var blob=new Blob(chunks,{type:mime});
			var reader=new FileReader();
			reader.onloadend=function(){
				endCall();
				True(reader.result,mime);
			};
			reader.readAsArrayBuffer(blob);
		};
		recorder.onerror=function(e){
			endCall();
			False($T("PIX0::转码webm出错：{1}",0,e.message));
		};
		recorder.start();
		
		//声音源
		var buffer=ctx.createBuffer(1,size,sampleRate);
		var buffer0=buffer.getChannelData(0);
		for(var j=0;j<size;j++){
			var s=res[j];
			s=s<0?s/0x8000:s/0x7FFF;
			buffer0[j]=s;
		};
		var source=ctx.createBufferSource();
		source.channelCount=1;
		source.buffer=buffer;
		source.connect(dest);
		if(source.start){source.start()}else{source.noteOn(0)};
		source.onended=function(){
			recorder.stop();
		};
	}
	
}));