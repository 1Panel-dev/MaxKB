/*
录音
https://github.com/xiangyuecn/Recorder
*/
(function(factory){
	var browser=typeof window=="object" && !!window.document;
	var win=browser?window:Object; //非浏览器环境，Recorder挂载在Object下面
	factory(win,browser);
	//umd returnExports.js
	if(typeof(define)=='function' && define.amd){
		define(function(){
			return win.Recorder;
		});
	};
	if(typeof(module)=='object' && module.exports){
		module.exports=win.Recorder;
	};
}(function(Export,isBrowser){
"use strict";

var NOOP=function(){};
var IsNum=function(v){return typeof v=="number"};
var ToJson=function(v){return JSON.stringify(v)};

var Recorder=function(set){
	return new initFn(set);
};
var LM=Recorder.LM="2025-01-11 09:28";
var GitUrl="https://github.com/xiangyuecn/Recorder";
var RecTxt="Recorder";
var getUserMediaTxt="getUserMedia";
var srcSampleRateTxt="srcSampleRate";
var sampleRateTxt="sampleRate";
var bitRateTxt="bitRate";
var CatchTxt="catch";

var WRec2=Export[RecTxt];//重复加载js
if(WRec2&&WRec2.LM==LM){
	WRec2.CLog(WRec2.i18n.$T("K8zP::重复导入{1}",0,RecTxt),3);
	return;
};


//是否已经打开了全局的麦克风录音，所有工作都已经准备好了，就等接收音频数据了
Recorder.IsOpen=function(){
	var stream=Recorder.Stream;
	if(stream){
		var tracks=Tracks_(stream), track=tracks[0];
		if(track){
			var state=track.readyState;
			return state=="live"||state==track.LIVE;
		};
	};
	return false;
};
/*H5录音时的AudioContext缓冲大小。会影响H5录音时的onProcess调用速率，相对于AudioContext.sampleRate=48000时，4096接近12帧/s，调节此参数可生成比较流畅的回调动画。
	取值256, 512, 1024, 2048, 4096, 8192, or 16384
	注意，取值不能过低，2048开始不同浏览器可能回调速率跟不上造成音质问题。
	一般无需调整，调整后需要先close掉已打开的录音，再open时才会生效。
*/
Recorder.BufferSize=4096;
//销毁已持有的所有全局资源，当要彻底移除Recorder时需要显式的调用此方法
Recorder.Destroy=function(){
	CLog(RecTxt+" Destroy");
	Disconnect();//断开可能存在的全局Stream、资源
	
	for(var k in DestroyList){
		DestroyList[k]();
	};
};
var DestroyList={};
//登记一个需要销毁全局资源的处理方法
Recorder.BindDestroy=function(key,call){
	DestroyList[key]=call;
};
//判断浏览器是否支持录音，随时可以调用。注意：仅仅是检测浏览器支持情况，不会判断和调起用户授权，不会判断是否支持特定格式录音。
Recorder.Support=function(){
	if(!isBrowser) return false;
	var scope=navigator.mediaDevices||{};
	if(!scope[getUserMediaTxt]){
		scope=navigator;
		scope[getUserMediaTxt]||(scope[getUserMediaTxt]=scope.webkitGetUserMedia||scope.mozGetUserMedia||scope.msGetUserMedia);
	};
	if(!scope[getUserMediaTxt]){
		return false;
	};
	Recorder.Scope=scope;
	
	if(!Recorder.GetContext()){
		return false;
	};
	return true;
};
//获取AudioContext对象，如果浏览器不支持将返回null。tryNew=false时返回全局的Recorder.Ctx，Ctx.state可能是closed，仅限用于解码等操作。tryNew=true时会尝试创建新的ctx（不支持close的老浏览器依旧返回全局的），注意用完必须自己调用CloseNewCtx(ctx)关闭；注意：非用户操作（触摸、点击等）时调用返回的ctx.state可能是suspended状态，需要在用户操作时调用ctx.resume恢复成running状态，参考rec的runningContext配置
Recorder.GetContext=function(tryNew){
	if(!isBrowser) return null;
	var AC=window.AudioContext;
	if(!AC){
		AC=window.webkitAudioContext;
	};
	if(!AC){
		return null;
	};
	
	var ctx=Recorder.Ctx, isNew=0;
	if(!ctx){ //241020版本后不再保留打开状态的ctx，原因是iOS不全部关闭时新的ctx有可能不正常
		//不能反复构造，低版本number of hardware contexts reached maximum (6)
		ctx=Recorder.Ctx=new AC(); isNew=1;
		Recorder.NewCtxs=Recorder.NewCtxs||[];
		
		Recorder.BindDestroy("Ctx",function(){
			var ctx=Recorder.Ctx;
			if(ctx&&ctx.close){//能关掉就关掉，关不掉就保留着
				CloseCtx(ctx);
				Recorder.Ctx=0;
			};
			var arr=Recorder.NewCtxs; Recorder.NewCtxs=[];
			for(var i=0;i<arr.length;i++)CloseCtx(arr[i]);
		});
	};
	if(tryNew && ctx.close){//没法关闭的不允许再创建
		if(!isNew){
			if(!ctx._useC) CloseCtx(ctx); //关闭全局的，不再保留打开状态
			ctx=new AC(); //如果是上面新建的就用上面的，不然就用全新的
		};
		ctx._useC=1;
		Recorder.NewCtxs.push(ctx);
	};
	return ctx;
};
//关闭新创建的AudioContext（之前老版本如果是全局的不关闭，241020版本后全部关闭）
Recorder.CloseNewCtx=function(ctx){
	if(ctx && ctx.close){
		CloseCtx(ctx);
		var arr=Recorder.NewCtxs||[],L=arr.length;
		for(var i=0;i<arr.length;i++){
			if(arr[i]==ctx){ arr.splice(i,1); break; }
		}
		CLog($T("mSxV::剩{1}个GetContext未close",0,L+"-1="+arr.length),arr.length?3:0);
	}
};
var CloseCtx=function(ctx){
	if(ctx && ctx.close && !ctx._isC){
		ctx._isC=1;
		if(ctx.state!="closed"){
			try{ ctx.close() }catch(e){ CLog("ctx close err",1,e) }
		}
	}
};
//当AudioContext的状态是suspended时，调用resume恢复状态，但如果没有用户操作resume可能没有回调，封装解决此回调问题；check(count)返回true继续尝试resume，返回false终止任务（不回调False）
var ResumeCtx=Recorder.ResumeCtx=function(ctx,check,True,False){
	var isEnd=0,isBind=0,isLsSC=0,runC=0,EL="EventListener",Tag="ResumeCtx ";
	var end=function(err,ok){
		if(isBind){ bind() }
		if(!isEnd){ isEnd=1; //回调结果
			err&&False(err,runC);
			ok&&True(runC);
		}
		if(ok){ //监听后续状态变化
			if(!ctx._LsSC && ctx["add"+EL]) ctx["add"+EL]("statechange",run);
			ctx._LsSC=1; isLsSC=1;
		}
	};
	var bind=function(add){
		if(add && isBind) return; isBind=add?1:0;
		var types=["focus","mousedown","mouseup","touchstart","touchend"];
		for(var i=0;i<types.length;i++)
			window[(add?"add":"remove")+EL](types[i],run,true);
	};
	var run=function(){
		var sVal=ctx.state,spEnd=CtxSpEnd(sVal);
		if(!isEnd && !check(spEnd?++runC:runC))return end(); //终止，不回调
		if(spEnd){
			if(isLsSC)CLog(Tag+"sc "+sVal,3);
			bind(1); //绑定用户事件尝试恢复
			ctx.resume().then(function(){ //resume回调不可靠
				if(isLsSC)CLog(Tag+"sc "+ctx.state);
				end(0,1);
			})[CatchTxt](function(e){ //出错且无法恢复
				CLog(Tag+"error",1,e);
				if(!CtxSpEnd(ctx.state)){
					end(e.message||"error");
				}
			});
		}else if(sVal=="closed"){
			if(isLsSC && !ctx._isC)CLog(Tag+"sc "+sVal,1); //无法恢复，打个日志
			end("ctx closed");
		}else{ end(0,1) }; //running 或老的无state
	};
	run();
};
var CtxSpEnd=Recorder.CtxSpEnd=function(v){
	return v=="suspended"||v=="interrupted"; //后面这个仅iOS有
};
var CtxState=function(ctx){
	var v=ctx.state,msg="ctx.state="+v;
	if(CtxSpEnd(v))msg+=$T("nMIy::（注意：ctx不是running状态，rec.open和start至少要有一个在用户操作(触摸、点击等)时进行调用，否则将在rec.start时尝试进行ctx.resume，可能会产生兼容性问题(仅iOS)，请参阅文档中runningContext配置）");
	return msg;
};


/*是否启用MediaRecorder.WebM.PCM来进行音频采集连接（如果浏览器支持的话），默认启用，禁用或者不支持时将使用AudioWorklet或ScriptProcessor来连接；MediaRecorder采集到的音频数据比其他方式更好，几乎不存在丢帧现象，所以音质明显会好很多，建议保持开启*/
var ConnectEnableWebM="ConnectEnableWebM";
Recorder[ConnectEnableWebM]=true;

/*是否启用AudioWorklet特性来进行音频采集连接（如果浏览器支持的话），默认禁用，禁用或不支持时将使用过时的ScriptProcessor来连接（如果方法还在的话），当前AudioWorklet的实现在移动端没有ScriptProcessor稳健；ConnectEnableWebM如果启用并且有效时，本参数将不起作用*/
var ConnectEnableWorklet="ConnectEnableWorklet";
Recorder[ConnectEnableWorklet]=false;

/*初始化H5音频采集连接。如果自行提供了sourceStream将只进行一次简单的连接处理。如果是普通麦克风录音，此时的Stream是全局的，Safari上断开后就无法再次进行连接使用，表现为静音，因此使用全部使用全局处理避免调用到disconnect；全局处理也有利于屏蔽底层细节，start时无需再调用底层接口，提升兼容、可靠性。*/
var Connect=function(streamStore){
	var bufferSize=streamStore.BufferSize||Recorder.BufferSize;
	
	var stream=streamStore.Stream;
	var ctx=stream._c, ctxSR=ctx[sampleRateTxt], srChunk={};
	
	//获取音频流信息
	var tracks=Tracks_(stream),track=tracks[0],trackSet=null,tsMsg="";
	if(track && track.getSettings){
		trackSet=track.getSettings();
		var trackSR=trackSet[sampleRateTxt];
		if(trackSR && trackSR!=ctxSR){
			tsMsg=$T("eS8i::Stream的采样率{1}不等于{2}，将进行采样率转换（注意：音质不会变好甚至可能变差），主要在移动端未禁用回声消除时会产生此现象，浏览器有回声消除时可能只会返回16k采样率的音频数据，",0,trackSR,ctxSR);
		}
	}
	stream._ts=trackSet;
	CLog(tsMsg+"Stream TrackSet: "+ToJson(trackSet), tsMsg?3:0);
	
	var mediaConn=function(node){
		var media=stream._m=ctx.createMediaStreamSource(stream);
		var ctxDest=ctx.destination,cmsdTxt="createMediaStreamDestination";
		if(ctx[cmsdTxt]){
			ctxDest=stream._d=ctx[cmsdTxt]();
		};
		media.connect(node);
		node.connect(ctxDest);
	}
	var isWebM,isWorklet,badInt,webMTips="";
	var calls=stream._call;
	
	//浏览器回传的音频数据处理
	var onReceive=function(float32Arr, arrSR){
		for(var k0 in calls){//has item
			if(arrSR!=ctxSR){ //MediaRecorder录制的采样率可能和ctx的采样率不同（16k），转换采样率方便统一处理代码也更简单，但音质不会变好，甚至可能会变差一点
				srChunk.index=0;
				srChunk=Recorder.SampleData([float32Arr],arrSR,ctxSR,srChunk,{_sum:1});
				var pcm=srChunk.data;
				var sum=srChunk._sum;
			}else{ //采样率相同，不需要转换采样率
				srChunk={};
				var size=float32Arr.length;
				
				var pcm=new Int16Array(size);
				var sum=0;
				for(var j=0;j<size;j++){//floatTo16BitPCM 
					var s=Math.max(-1,Math.min(1,float32Arr[j]));
					s=s<0?s*0x8000:s*0x7FFF;
					pcm[j]=s;
					sum+=Math.abs(s);
				};
			};
			
			for(var k in calls){
				calls[k](pcm,sum);
			};
			
			return;
		};
	};
	
	var scriptProcessor="ScriptProcessor";//一堆字符串名字，有利于压缩js
	var audioWorklet="audioWorklet";
	var recAudioWorklet=RecTxt+" "+audioWorklet;
	var RecProc="RecProc";
	var MediaRecorderTxt="MediaRecorder";
	var MRWebMPCM=MediaRecorderTxt+".WebM.PCM";


//===================连接方式三=========================
	//古董级别的 ScriptProcessor 处理，目前所有浏览器均兼容，虽然是过时的方法，但更稳健，移动端性能比AudioWorklet强
	var oldFn=ctx.createScriptProcessor||ctx.createJavaScriptNode;
	var oldIsBest=$T("ZGlf::。由于{1}内部1秒375次回调，在移动端可能会有性能问题导致回调丢失录音变短，PC端无影响，暂不建议开启{1}。",0,audioWorklet);
	var oldScript=function(){
		isWorklet=stream.isWorklet=false;
		_Disconn_n(stream);
		CLog($T("7TU0::Connect采用老的{1}，",0,scriptProcessor)
			+i18n.get(Recorder[ConnectEnableWorklet]?
				$T("JwCL::但已设置{1}尝试启用{2}",2)
				:$T("VGjB::可设置{1}尝试启用{2}",2)
				,[RecTxt+"."+ConnectEnableWorklet+"=true",audioWorklet]
			)+webMTips+oldIsBest,3);
		
		var process=stream._p=oldFn.call(ctx,bufferSize,1,1);//单声道，省的数据处理复杂
		mediaConn(process);
		
		process.onaudioprocess=function(e){
			var arr=e.inputBuffer.getChannelData(0);
			onReceive(arr, ctxSR);
		};
	};


//===================连接方式二=========================
var connWorklet=function(){
	//尝试开启AudioWorklet处理
	isWebM=stream.isWebM=false;
	_Disconn_r(stream);
	
	isWorklet=stream.isWorklet=!oldFn || Recorder[ConnectEnableWorklet];
	var AwNode=window.AudioWorkletNode;
	if(!(isWorklet && ctx[audioWorklet] && AwNode)){
		oldScript();//被禁用 或 不支持，直接使用老的
		return;
	};
	var clazzUrl=function(){
		var xf=function(f){return f.toString().replace(/^function|DEL_/g,"").replace(/\$RA/g,recAudioWorklet)};
		var clazz='class '+RecProc+' extends AudioWorkletProcessor{';
			clazz+="constructor "+xf(function(option){
				DEL_super(option);
				var This=this,bufferSize=option.processorOptions.bufferSize;
				This.bufferSize=bufferSize;
				This.buffer=new Float32Array(bufferSize*2);//乱给size搞乱缓冲区不管
				This.pos=0;
				This.port.onmessage=function(e){
					if(e.data.kill){
						This.kill=true;
						$C.log("$RA kill call");
					}
				};
				$C.log("$RA .ctor call", option);
			});
			
			//https://developer.mozilla.org/en-US/docs/Web/API/AudioWorkletProcessor/process 每次回调128个采样数据，1秒375次回调，高频导致移动端性能问题，结果就是回调次数缺斤少两，进而导致丢失数据，PC端似乎没有性能问题
			clazz+="process "+xf(function(input,b,c){//需要等到ctx激活后才会有回调
				var This=this,bufferSize=This.bufferSize;
				var buffer=This.buffer,pos=This.pos;
				input=(input[0]||[])[0]||[];
				if(input.length){
					buffer.set(input,pos);
					pos+=input.length;
					
					var len=~~(pos/bufferSize)*bufferSize;
					if(len){
						this.port.postMessage({ val: buffer.slice(0,len) });
						
						var more=buffer.subarray(len,pos);
						buffer=new Float32Array(bufferSize*2);
						buffer.set(more);
						pos=more.length;
						This.buffer=buffer;
					}
					This.pos=pos;
				}
				return !This.kill;
			});
		clazz+='}'
			+'try{'
				+'registerProcessor("'+RecProc+'", '+RecProc+')'
			+'}catch(e){$C.error("'+recAudioWorklet+' Reg Error",e)}';
		clazz=clazz.replace(/\$C\./g,"console.");//一些编译器会文本替换日志函数
		//URL.createObjectURL 本地有些浏览器会报 Not allowed to load local resource，直接用dataurl
		return "data:text/javascript;base64,"+btoa(unescape(encodeURIComponent(clazz)));
	};
	
	var awNext=function(){//可以继续，没有调用断开
		return isWorklet && stream._na;
	};
	var nodeAlive=stream._na=function(){
		//start时会调用，只要没有收到数据就断定AudioWorklet有问题，恢复用老的
		if(badInt!==""){//没有回调过数据
			clearTimeout(badInt);
			badInt=setTimeout(function(){
				badInt=0;
				if(awNext()){
					CLog($T("MxX1::{1}未返回任何音频，恢复使用{2}",0,audioWorklet,scriptProcessor),3);
					oldFn&&oldScript();//未来没有老的，可能是误判
				};
			},500);
		};
	};
	var createNode=function(){
		if(!awNext())return;
		var node=stream._n=new AwNode(ctx, RecProc, {
			processorOptions:{bufferSize:bufferSize}
		});
		mediaConn(node);
		node.port.onmessage=function(e){
			if(badInt){
				clearTimeout(badInt);badInt="";
			};
			if(awNext()){
				onReceive(e.data.val, ctxSR);
			}else if(!isWorklet){
				CLog($T("XUap::{1}多余回调",0,audioWorklet),3);
			};
		};
		CLog($T("yOta::Connect采用{1}，设置{2}可恢复老式{3}",0,audioWorklet,RecTxt+"."+ConnectEnableWorklet+"=false",scriptProcessor)+webMTips+oldIsBest,3);
	};
	
	//如果start时的resume和下面的构造node同时进行，将会导致部分浏览器崩溃 (STATUS_ACCESS_VIOLATION)，源码assets中 ztest_chrome_bug_AudioWorkletNode.html 可测试。所以，将所有代码套到resume里面（不管catch），避免出现这个问题
	var ctxOK=function(){
		if(!awNext())return;
		if(ctx[RecProc]){
			createNode();
			return;
		};
		var url=clazzUrl();
		ctx[audioWorklet].addModule(url).then(function(e){
			if(!awNext())return;
			ctx[RecProc]=1;
			createNode();
			if(badInt){//重新计时
				nodeAlive();
			};
		})[CatchTxt](function(e){ //fix 关键字，保证catch压缩时保持字符串形式
			CLog(audioWorklet+".addModule Error",1,e);
			awNext()&&oldScript();
		});
	};
	ResumeCtx(ctx,function(){ return awNext() } ,ctxOK,ctxOK);
};


//===================连接方式一=========================
var connWebM=function(){
	//尝试开启MediaRecorder录制webm+pcm处理
	var MR=window[MediaRecorderTxt];
	var onData="ondataavailable";
	var webmType="audio/webm; codecs=pcm";
	isWebM=stream.isWebM=Recorder[ConnectEnableWebM];
	
	var supportMR=MR && (onData in MR.prototype) && MR.isTypeSupported(webmType);
	webMTips=supportMR?"":$T("VwPd::（此浏览器不支持{1}）",0,MRWebMPCM);
	if(!isWebM || !supportMR){
		connWorklet(); //被禁用 或 不支持MediaRecorder 或 不支持webm+pcm
		return;
	}
	
	var mrNext=function(){//可以继续，没有调用断开
		return isWebM && stream._ra;
	};
	stream._ra=function(){
		//start时会调用，只要没有收到数据就断定MediaRecorder有问题，降级处理
		if(badInt!==""){//没有回调过数据
			clearTimeout(badInt);
			badInt=setTimeout(function(){
				//badInt=0; 保留给nodeAlive继续判断
				if(mrNext()){
					CLog($T("vHnb::{1}未返回任何音频，降级使用{2}",0,MediaRecorderTxt,audioWorklet),3);
					connWorklet();
				};
			},500);
		};
	};
	
	var mrSet=Object.assign({mimeType:webmType}, Recorder.ConnectWebMOptions);
	var mr=stream._r=new MR(stream, mrSet);
	var webmData=stream._rd={};
	mr[onData]=function(e){
		//提取webm中的pcm数据，提取失败就等着badInt超时降级处理
		var reader=new FileReader();
		reader.onloadend=function(){
			if(mrNext()){
				var f32arr=WebM_Extract(new Uint8Array(reader.result),webmData);
				if(!f32arr)return;
				if(f32arr==-1){//无法提取，立即降级
					connWorklet();
					return;
				};
				
				if(badInt){
					clearTimeout(badInt);badInt="";
				};
				onReceive(f32arr, webmData.webmSR);
			}else if(!isWebM){
				CLog($T("O9P7::{1}多余回调",0,MediaRecorderTxt),3);
			};
		};
		reader.readAsArrayBuffer(e.data);
	};
	try{
		mr.start(~~(bufferSize/48));//按48k时的回调间隔
		CLog($T("LMEm::Connect采用{1}，设置{2}可恢复使用{3}或老式{4}",0,MRWebMPCM,RecTxt+"."+ConnectEnableWebM+"=false",audioWorklet,scriptProcessor));
	}catch(e){ //存在视频流时可能会抛异常
		CLog("mr start err",1,e);
		connWorklet();
	};
};

	connWebM();
};
var ConnAlive=function(stream){
	if(stream._na) stream._na(); //检查AudioWorklet连接是否有效，无效就回滚到老的ScriptProcessor
	if(stream._ra) stream._ra(); //检查MediaRecorder连接是否有效，无效就降级处理
};
var _Disconn_n=function(stream){
	stream._na=null;
	if(stream._n){
		stream._n.port.postMessage({kill:true});
		stream._n.disconnect();
		stream._n=null;
	};
};
var _Disconn_r=function(stream){
	stream._ra=null;
	if(stream._r){
		try{ stream._r.stop() }catch(e){ CLog("mr stop err",1,e) }
		stream._r=null;
	};
};
var Disconnect=function(streamStore){
	streamStore=streamStore||Recorder;
	var isGlobal=streamStore==Recorder;
	
	var stream=streamStore.Stream;
	if(stream){
		if(stream._m){
			stream._m.disconnect();
			stream._m=null;
		};
		if(!stream._RC && stream._c){//提供的runningContext不处理
			Recorder.CloseNewCtx(stream._c);
		};
		stream._RC=null; stream._c=null;
		if(stream._d){
			StopS_(stream._d.stream);
			stream._d=null;
		};
		if(stream._p){
			stream._p.disconnect();
			stream._p.onaudioprocess=stream._p=null;
		};
		_Disconn_n(stream);
		_Disconn_r(stream);
		
		if(isGlobal){//全局的时候，要把流关掉（麦克风），直接提供的流不处理
			StopS_(stream);
		};
	};
	streamStore.Stream=0;
};
//关闭一个音频流
var StopS_=Recorder.StopS_=function(stream){
	var tracks=Tracks_(stream);
	for(var i=0;i<tracks.length;i++){
		var track=tracks[i];
		track.stop&&track.stop();
	};
	stream.stop&&stream.stop();
};
//获取流中的所有轨道
var Tracks_=function(stream){
	var arr1=0,arr2=0,arr=[];
	//stream.getTracks() 得到的sourceStream还得去排序 不然第一个可能是video
	if(stream.getAudioTracks){ arr1=stream.getAudioTracks(); arr2=stream.getVideoTracks(); }
	if(!arr1){ arr1=stream.audioTracks; arr2=stream.videoTracks; }
	for(var i=0,L=arr1?arr1.length:0;i<L;i++)arr.push(arr1[i]); //音频放前面，方便取[0]
	for(var i=0,L=arr2?arr2.length:0;i<L;i++)arr.push(arr2[i]);
	return arr;
};

/*对pcm数据的采样率进行转换
pcmDatas: [[Int16,...]] pcm片段列表，二维数组里面是Int16Array，也可传Float32Array（会转成Int16Array）
pcmSampleRate:48000 pcm数据的采样率
newSampleRate:16000 需要转换成的采样率，241020版本后支持转成任意采样率，之前老版本newSampleRate>=pcmSampleRate时不会进行任何处理，小于时会进行重新采样
prevChunkInfo:{} 可选，上次调用时的返回值，用于连续转换，本次调用将从上次结束位置开始进行处理。或可自行定义一个ChunkInfo从pcmDatas指定的位置开始进行转换
option:{ 可选，配置项
		frameSize:123456 帧大小，每帧的PCM Int16的数量，采样率转换后的pcm长度为frameSize的整数倍，用于连续转换。目前仅在mp3格式时才有用，frameSize取值为1152，这样编码出来的mp3时长和pcm的时长完全一致，否则会因为mp3最后一帧录音不够填满时添加填充数据导致mp3的时长变长。
		frameType:"" 帧类型，一般为rec.set.type，提供此参数时无需提供frameSize，会自动使用最佳的值给frameSize赋值，目前仅支持mp3=1152(MPEG1 Layer3的每帧采采样数)，其他类型=1。
			以上两个参数用于连续转换时使用，最多使用一个，不提供时不进行帧的特殊处理，提供时必须同时提供prevChunkInfo才有作用。最后一段数据处理时无需提供帧大小以便输出最后一丁点残留数据。
	}

返回ChunkInfo:{
	//可定义，从指定位置开始转换到结尾
	index:0 pcmDatas已处理到的索引；比如每次都是单个pcm需要连续处理时，可每次调用前重置成0，pcmDatas仅需传入`[pcm]`固定一个元素
	offset:0.0 已处理到的index对应的pcm中的偏移的下一个位置（提升采样率时为结果的pcm）
	raisePrev:null 提升采样率时的前一个pcm结果采样值
	
	//可定义，指定的一个滤波配置：默认使用Recorder.IIRFilter低通滤波（可有效抑制混叠产生的杂音，小采样率大于高采样率的75%时不默认滤波），如果提供了配置但fn为null时将不滤波；sr、srn为此滤波函数对应的初始化采样率，当采样率和参数的不一致时将重新设为默认函数
	filter:null||{fn:fn(sample),sr:pcmSampleRate,srn:newSampleRate}
	
	//仅作为返回值
	frameNext:null||[Int16,...] 下一帧的部分数据，frameSize设置了的时候才可能会有
	sampleRate:16000 结果的采样率=newSampleRate，老版本<=newSampleRate
	data:[Int16,...] 转换后的PCM结果；如果是连续转换，并且pcmDatas中并没有新数据时，data的长度可能为0
}
*/
Recorder.SampleData=function(pcmDatas,pcmSampleRate,newSampleRate,prevChunkInfo,option){
	var Txt="SampleData";
	prevChunkInfo||(prevChunkInfo={});
	var index=prevChunkInfo.index||0;
	var offset=prevChunkInfo.offset||0;
	var raisePrev=prevChunkInfo.raisePrev||0;
	
	var filter=prevChunkInfo.filter;
	if(filter&&filter.fn&&(filter.sr&&filter.sr!=pcmSampleRate || filter.srn&&filter.srn!=newSampleRate)){
		filter=null; CLog($T("d48C::{1}的filter采样率变了，重设滤波",0,Txt),3);
	};
	if(!filter){ //采样率差距比较大才开启低通滤波
		if(newSampleRate<=pcmSampleRate){ //降低采样率或不变，最高频率用新采样率频率的3/4
			var freq=newSampleRate>pcmSampleRate*3/4?0: newSampleRate/2 *3/4;
			filter={fn:freq?Recorder.IIRFilter(true,pcmSampleRate,freq):0};
		}else{ //提升采样率，最高频率用原始采样率频率的3/4
			var freq=pcmSampleRate>newSampleRate*3/4?0: pcmSampleRate/2 *3/4;
			filter={fn:freq?Recorder.IIRFilter(true,newSampleRate,freq):0};
		};
	};
	filter.sr=pcmSampleRate;
	filter.srn=newSampleRate;
	var filterFn=filter.fn;
	
	var frameNext=prevChunkInfo.frameNext||[];
	option||(option={});
	var frameSize=option.frameSize||1;
	if(option.frameType){
		frameSize=option.frameType=="mp3"?1152:1;
	};
	var useSum=option._sum, _sum=0; //内部用的，sum不考虑配置了frame
	
	var nLen=pcmDatas.length;
	if(index>nLen+1){
		CLog($T("tlbC::{1}似乎传入了未重置chunk {2}",0,Txt,index+">"+nLen),3);
	};
	var size=0;
	for(var i=index;i<nLen;i++){
		size+=pcmDatas[i].length;
	};
	
	//采样 https://www.cnblogs.com/blqw/p/3782420.html
	var step=pcmSampleRate/newSampleRate;
	if(step>1){//新采样低于录音采样，进行抽样
		size=Math.max(0,size-Math.floor(offset));
		size=Math.floor(size/step);
	}else if(step<1){//新采样高于录音采样，插值处理
		var raiseStep=1/step;
		size=Math.floor(size*raiseStep);
	};
	
	size+=frameNext.length;
	var res=new Int16Array(size);
	var idx=0;
	//添加上一次不够一帧的剩余数据
	for(var i=0;i<frameNext.length;i++){
		res[idx]=frameNext[i];
		idx++;
	};
	//处理数据
	for (;index<nLen;index++) {
		var o=pcmDatas[index], isF32=o instanceof Float32Array;
		var i=offset,il=o.length;
		var F=filterFn&&filterFn.Embed,F1=0,F2=0,Fx=0,Fy=0;//低通滤波后的数据
		
		if(step<1){ //提升采样率
			var idx1=idx+i, prev=raisePrev;
			for(var i0=0;i0<il;i0++){
				var oVal=o[i0];
				if(isF32){//floatTo16BitPCM 
					oVal=Math.max(-1,Math.min(1,oVal));
					oVal=oVal<0?oVal*0x8000:oVal*0x7FFF;
				}
				
				var pos=Math.floor(idx1);
				idx1+=raiseStep;
				var end=Math.floor(idx1);
			
				//简单的从prev平滑填充到cur，有效减少转换引入的杂音
				var n=(oVal-prev)/(end-pos);
				for(var j=1;pos<end;pos++,j++){
					var s=Math.floor(prev+(j*n));
					if(F){//IIRFilter代码内置，比函数调用快4倍
						Fx=s;
						Fy=F.b0 * Fx + F.b1 * F.x1 + F.b0 * F.x2 - F.a1 * F.y1 - F.a2 * F.y2;
						F.x2 = F.x1; F.x1 = Fx; F.y2 = F.y1; F.y1 = Fy;
						s=Fy;
					}else{ s=filterFn?filterFn(s):s; }
					
					if(s>0x7FFF) s=0x7FFF; else if(s<-0x8000) s=-0x8000; //Int16越界处理
					if(useSum) _sum+=Math.abs(s);
					res[pos]=s;
					idx++;
				};
				
				prev=raisePrev=oVal;
				i+=raiseStep;//插值
			}
			offset=i%1;
			continue;
		};
		//降低采样率或不变
		for(var i0=0,i2=0;i0<il;i0++,i2++){
			if(i2<il){
				var oVal=o[i2];
				if(isF32){//floatTo16BitPCM 
					oVal=Math.max(-1,Math.min(1,oVal));
					oVal=oVal<0?oVal*0x8000:oVal*0x7FFF;
				}
				if(F){//IIRFilter代码内置，比函数调用快4倍
					Fx=oVal;
					Fy=F.b0 * Fx + F.b1 * F.x1 + F.b0 * F.x2 - F.a1 * F.y1 - F.a2 * F.y2;
					F.x2 = F.x1; F.x1 = Fx; F.y2 = F.y1; F.y1 = Fy;
				}else{ Fy=filterFn?filterFn(oVal):oVal; }
			}
			F1=F2; F2=Fy;
			if(i2==0){ i0--; continue; } //首次只计算o[0]
			
			//https://www.cnblogs.com/xiaoqi/p/6993912.html
			//当前点=当前点+到后面一个点之间的增量，音质比直接简单抽样好些
			var before = Math.floor(i);
			if(i0!=before)continue;
			var after = Math.ceil(i);
			var atPoint = i - before;
			
			var beforeVal=F1;
			var afterVal=after<il ? F2 : beforeVal; //后个点越界了，忽略不计
			var val=beforeVal+(afterVal-beforeVal)*atPoint;
			
			if(val>0x7FFF) val=0x7FFF; else if(val<-0x8000) val=-0x8000; //Int16越界处理
			if(useSum) _sum+=Math.abs(val);
			res[idx]=val;
			
			idx++;
			i+=step;//抽样
		};
		offset=Math.max(0, i-il); //不太可能出现负数
	};
	if(step<1 && idx+1==size){ //提升采样率时可能缺1个，直接删除结尾1个
		size--; res=new Int16Array(res.buffer.slice(0, size*2));
	};
	if(idx-1!=size && idx!=size)CLog(Txt+" idx:"+idx+" != size:"+size,3); //越界1个
	
	//帧处理
	frameNext=null;
	var frameNextSize=size%frameSize;
	if(frameNextSize>0){
		var u8Pos=(size-frameNextSize)*2;
		frameNext=new Int16Array(res.buffer.slice(u8Pos));
		res=new Int16Array(res.buffer.slice(0,u8Pos));
	};
	
	var obj={
		index:index
		,offset:offset
		,raisePrev:raisePrev
		,filter:filter
		
		,frameNext:frameNext
		,sampleRate:newSampleRate
		,data:res
	};
	if(useSum) obj._sum=_sum;
	return obj;
};

/*IIR低通、高通滤波，移植自：https://gitee.com/52jian/digital-audio-filter AudioFilter.java
	useLowPass: true或false，true为低通滤波，false为高通滤波
	sampleRate: 待处理pcm的采样率
	freq: 截止频率Hz，最大频率为sampleRate/2，低通时会切掉高于此频率的声音，高通时会切掉低于此频率的声音，注意滤波并非100%的切掉不需要的声音，而是减弱频率对应的声音，离截止频率越远对应声音减弱越厉害，离截止频率越近声音就几乎无衰减
	返回的是一个函数，用此函数对pcm的每个采样值按顺序进行处理即可（不同pcm不可共用）；注意此函数返回值可能会越界超过Int16范围，自行限制一下即可：Math.min(Math.max(val,-0x8000),0x7FFF)
可重新赋值一个函数，来改变Recorder的默认行为，比如SampleData中的低通滤波*/
Recorder.IIRFilter=function(useLowPass, sampleRate, freq){
	var ov = 2 * Math.PI * freq / sampleRate;
	var sn = Math.sin(ov);
	var cs = Math.cos(ov);
	var alpha = sn / 2;
	
	var a0 = 1 + alpha;
	var a1 = (-2 * cs) / a0;
	var a2 = (1 - alpha) / a0;
	if(useLowPass){
		var b0 = (1 - cs) / 2 / a0;
		var b1 = (1 - cs) / a0;
	}else{
		var b0 = (1 + cs) / 2 / a0;
		var b1 = -(1 + cs) / a0;
	}
	
	var x1=0,x2=0,y=0,y1=0,y2=0;
	var fn=function(x){
		y = b0 * x + b1 * x1 + b0 * x2 - a1 * y1 - a2 * y2;
		x2 = x1; x1 = x;
		y2 = y1; y1 = y;
		return y;
	};
	fn.Embed={x1:0,x2:0,y1:0,y2:0,b0:b0,b1:b1,a1:a1,a2:a2};
	return fn;
};


/*计算音量百分比的一个方法
pcmAbsSum: pcm Int16所有采样的绝对值的和
pcmLength: pcm长度
返回值：0-100，主要当做百分比用
注意：这个不是分贝，因此没用volume当做名称*/
Recorder.PowerLevel=function(pcmAbsSum,pcmLength){
	/*计算音量 https://blog.csdn.net/jody1989/article/details/73480259
	更高灵敏度算法:
		限定最大感应值10000
			线性曲线：低音量不友好
				power/10000*100 
			对数曲线：低音量友好，但需限定最低感应值
				(1+Math.log10(power/10000))*100
	*/
	var power=(pcmAbsSum/pcmLength) || 0;//NaN
	var level;
	if(power<1251){//1250的结果10%，更小的音量采用线性取值
		level=Math.round(power/1250*10);
	}else{
		level=Math.round(Math.min(100,Math.max(0,(1+Math.log(power/10000)/Math.log(10))*100)));
	};
	return level;
};

/*计算音量，单位dBFS（满刻度相对电平）
maxSample: 为16位pcm采样的绝对值中最大的一个（计算峰值音量），或者为pcm中所有采样的绝对值的平局值
返回值：-100~0 （最大值0dB，最小值-100代替-∞）
*/
Recorder.PowerDBFS=function(maxSample){
	var val=Math.max(0.1, maxSample||0),Pref=0x7FFF;
	val=Math.min(val,Pref);
	//https://www.logiclocmusic.com/can-you-tell-the-decibel/
	//https://blog.csdn.net/qq_17256689/article/details/120442510
	val=20*Math.log(val/Pref)/Math.log(10);
	return Math.max(-100,Math.round(val));
};




//带时间的日志输出，可设为一个空函数来屏蔽日志输出
//CLog(msg,errOrLogMsg, logMsg...) err为数字时代表日志类型1:error 2:log默认 3:warn，否则当做内容输出，第一个参数不能是对象因为要拼接时间，后面可以接无数个输出参数
Recorder.CLog=function(msg,err){
	if(typeof console!="object")return;
	var now=new Date();
	var t=("0"+now.getMinutes()).substr(-2)
		+":"+("0"+now.getSeconds()).substr(-2)
		+"."+("00"+now.getMilliseconds()).substr(-3);
	var recID=this&&this.envIn&&this.envCheck&&this.id;
	var arr=["["+t+" "+RecTxt+(recID?":"+recID:"")+"]"+msg];
	var a=arguments,cwe=Recorder.CLog;
	var i=2,fn=cwe.log||console.log;
	if(IsNum(err)){
		fn=err==1?cwe.error||console.error:err==3?cwe.warn||console.warn:fn;
	}else{
		i=1;
	};
	for(;i<a.length;i++){
		arr.push(a[i]);
	};
	if(IsLoser){//古董浏览器，仅保证基本的可执行不代码异常
		fn&&fn("[IsLoser]"+arr[0],arr.length>1?arr:"");
	}else{
		fn.apply(console,arr);
	};
};
var CLog=function(){ Recorder.CLog.apply(this,arguments); };
var IsLoser=true;try{IsLoser=!console.log.apply;}catch(e){};




var ID=0;
function initFn(set){
	var This=this; This.id=++ID;
	
	//如果开启了流量统计，这里将发送一个图片请求
	Traffic();
	
	
	var o={
		type:"mp3" //输出类型：mp3,wav，wav输出文件尺寸超大不推荐使用，但mp3编码支持会导致js文件超大，如果不需支持mp3可以使js文件大幅减小
		//,bitRate:16 //比特率 wav:16或8位，MP3：8kbps 1k/s，8kbps 2k/s 录音文件很小
		
		//,sampleRate:16000 //采样率，wav格式大小=sampleRate*时间；mp3此项对低比特率有影响，高比特率几乎无影响。
					//wav任意值，mp3取值范围：48000, 44100, 32000, 24000, 22050, 16000, 12000, 11025, 8000
					//采样率参考https://www.cnblogs.com/devin87/p/mp3-recorder.html
		
		,onProcess:NOOP //fn(buffers,powerLevel,bufferDuration,bufferSampleRate,newBufferIdx,asyncEnd) buffers=[[Int16,...],...]：缓冲的PCM数据，为从开始录音到现在的所有pcm片段；powerLevel：当前缓冲的音量级别0-100，bufferDuration：已缓冲时长，bufferSampleRate：缓冲使用的采样率（当type支持边录边转码(Worker)时，此采样率和设置的采样率相同，否则不一定相同）；newBufferIdx:本次回调新增的buffer起始索引；asyncEnd:fn() 如果onProcess是异步的(返回值为true时)，处理完成时需要调用此回调，如果不是异步的请忽略此参数，此方法回调时必须是真异步（不能真异步时需用setTimeout包裹）。onProcess返回值：如果返回true代表开启异步模式，在某些大量运算的场合异步是必须的，必须在异步处理完成时调用asyncEnd(不能真异步时需用setTimeout包裹)，在onProcess执行后新增的buffer会全部替换成空数组，因此本回调开头应立即将newBufferIdx到本次回调结尾位置的buffer全部保存到另外一个数组内，处理完成后写回buffers中本次回调的结尾位置。
		
		//*******高级设置******
		//,sourceStream:MediaStream Object
				//可选直接提供一个媒体流，从这个流中录制、实时处理音频数据（当前Recorder实例独享此流）；不提供时为普通的麦克风录音，由getUserMedia提供音频流（所有Recorder实例共享同一个流）
				//比如：audio、video标签dom节点的captureStream方法（实验特性，不同浏览器支持程度不高）返回的流；WebRTC中的remote流；自己创建的流等
				//注意：流内必须至少存在一条音轨(Audio Track)，比如audio标签必须等待到可以开始播放后才会有音轨，否则open会失败
		
		//,runningContext:AudioContext
				//可选提供一个state为running状态的AudioContext对象(ctx)；默认会在rec.open时自动创建一个新的ctx，无用户操作（触摸、点击等）时调用rec.open的ctx.state可能为suspended，会在rec.start时尝试进行ctx.resume，如果也无用户操作ctx.resume可能不会恢复成running状态（目前仅iOS上有此兼容性问题），导致无法去读取媒体流，这时请提前在用户操作时调用Recorder.GetContext(true)来得到一个running状态AudioContext（用完需调用CloseNewCtx(ctx)关闭）
		
		//,audioTrackSet:{ deviceId:"",groupId:"", autoGainControl:true, echoCancellation:true, noiseSuppression:true }
				//普通麦克风录音时getUserMedia方法的audio配置参数，比如指定设备id，回声消除、降噪开关；注意：提供的任何配置值都不一定会生效
				//由于麦克风是全局共享的，所以新配置后需要close掉以前的再重新open
				//同样可配置videoTrackSet，更多参考: https://developer.mozilla.org/en-US/docs/Web/API/MediaTrackConstraints
		
		//,disableEnvInFix:false 内部参数，禁用设备卡顿时音频输入丢失补偿功能
		
		//,takeoffEncodeChunk:NOOP //fn(chunkBytes) chunkBytes=[Uint8,...]：实时编码环境下接管编码器输出，当编码器实时编码出一块有效的二进制音频数据时实时回调此方法；参数为二进制的Uint8Array，就是编码出来的音频数据片段，所有的chunkBytes拼接在一起即为完整音频。本实现的想法最初由QQ2543775048提出
				//当提供此回调方法时，将接管编码器的数据输出，编码器内部将放弃存储生成的音频数据；如果当前编码器或环境不支持实时编码处理，将在open时直接走fail逻辑
				//因此提供此回调后调用stop方法将无法获得有效的音频数据，因为编码器内没有音频数据，因此stop时返回的blob将是一个字节长度为0的blob
				//大部分录音格式编码器都支持实时编码（边录边转码），比如mp3格式：会实时的将编码出来的mp3片段通过此方法回调，所有的chunkBytes拼接到一起即为完整的mp3，此种拼接的结果比mock方法实时生成的音质更加，因为天然避免了首尾的静默
				//不支持实时编码的录音格式不可以提供此回调（wav格式不支持，因为wav文件头中需要提供文件最终长度），提供了将在open时直接走fail逻辑
	};
	
	for(var k in set){
		o[k]=set[k];
	};
	This.set=o;
	
	var vB=o[bitRateTxt],vS=o[sampleRateTxt]; //校验配置参数
	if(vB&&!IsNum(vB) || vS&&!IsNum(vS)){
		This.CLog($T.G("IllegalArgs-1",[$T("VtS4::{1}和{2}必须是数值",0,sampleRateTxt,bitRateTxt)]),1,set);
	};
	o[bitRateTxt]=+vB||16;
	o[sampleRateTxt]=+vS||16000;
	
	This.state=0;//运行状态，0未录音 1录音中 2暂停 3等待ctx激活
	This._S=9;//stop同步锁，stop可以阻止open过程中还未运行的start
	This.Sync={O:9,C:9};//和Recorder.Sync一致，只不过这个是非全局的，仅用来简化代码逻辑，无实际作用
};
//同步锁，控制对Stream的竞争；用于close时中断异步的open；一个对象open如果变化了都要阻止close，Stream的控制权交个新的对象
Recorder.Sync={/*open*/O:9,/*close*/C:9};

Recorder.prototype=initFn.prototype={
	CLog:CLog
	
	//流相关的数据存储在哪个对象里面；如果提供了sourceStream，数据直接存储在当前对象中，否则存储在全局
	,_streamStore:function(){
		if(this.set.sourceStream){
			return this;
		}else{
			return Recorder;
		}
	}
	//当前实例用到的Stream，可能是全局的，也可能是独享的
	,_streamGet:function(){
		return this._streamStore().Stream;
	}
	//当前实例用到的AudioContext，可能是全局的，也可能是独享的
	,_streamCtx:function(){
		var m=this._streamGet();
		return m&&m._c;
	}
	
	//打开录音资源True(),False(msg,isUserNotAllow)，需要调用close。注意：此方法是异步的；一般使用时打开，用完立即关闭；可重复调用，可用来测试是否能录音；open和start至少有一个应当在用户操作（触摸、点击等）下进行调用，原因参考runningContext配置
	,open:function(True,False){
		var This=this,set=This.set,streamStore=This._streamStore(),newCtx=0;
		True=True||NOOP;
		var failCall=function(errMsg,isUserNotAllow){
			isUserNotAllow=!!isUserNotAllow;
			This.CLog($T("5tWi::录音open失败：")+errMsg+",isUserNotAllow:"+isUserNotAllow,1);
			if(newCtx)Recorder.CloseNewCtx(newCtx);
			False&&False(errMsg,isUserNotAllow);
		};
		
		This._streamTag=getUserMediaTxt;
		var ok=function(){
			This.CLog("open ok, id:"+This.id+" stream:"+This._streamTag);
			True();
			
			This._SO=0;//解除stop对open中的start调用的阻止
		};
		
		
		//同步锁
		var Lock=streamStore.Sync;
		var lockOpen=++Lock.O,lockClose=Lock.C;
		This._O=This._O_=lockOpen;//记住当前的open，如果变化了要阻止close，这里假定了新对象已取代当前对象并且不再使用
		This._SO=This._S;//记住open过程中的stop，中途任何stop调用后都不能继续open中的start
		var lockFail=function(){
			//允许多次open，但不允许任何一次close，或者自身已经调用了关闭
			if(lockClose!=Lock.C || !This._O){
				var err=$T("dFm8::open被取消");
				if(lockOpen==Lock.O){
					//无新的open，已经调用了close进行取消，此处应让上次的close明确生效
					This.close();
				}else{
					err=$T("VtJO::open被中断");
				};
				failCall(err);
				return true;
			};
		};
		
		//环境配置检查
		if(!isBrowser){
			failCall($T.G("NonBrowser-1",["open"])+$T("EMJq::，可尝试使用RecordApp解决方案")+"("+GitUrl+"/tree/master/app-support-sample)");
			return;
		};
		var checkMsg=This.envCheck({envName:"H5",canProcess:true});
		if(checkMsg){
			failCall($T("A5bm::不能录音：")+checkMsg);
			return;
		};
		
		//尽量先创建好ctx，不然异步下创建可能不是running状态
		var ctx;
		var getCtx=function(){
			ctx=set.runningContext;
			if(!ctx)ctx=newCtx=Recorder.GetContext(true); //2023-06 尽量创建新的ctx，免得Safari再次连接无回调
		};
		
		//***********已直接提供了音频流************
		if(set.sourceStream){
			This._streamTag="set.sourceStream";
			if(!Recorder.GetContext()){
				failCall($T("1iU7::不支持此浏览器从流中获取录音"));
				return;
			};
			getCtx();
			
			Disconnect(streamStore);//可能已open过，直接先尝试断开
			var stream=This.Stream=set.sourceStream;
			stream._c=ctx;
			stream._RC=set.runningContext;
			stream._call={};
			
			try{
				Connect(streamStore);
			}catch(e){
				Disconnect(streamStore);
				failCall($T("BTW2::从流中打开录音失败：")+e.message);
				return;
			}
			ok();
			return;
		};
		
		
		//***********打开麦克风得到全局的音频流************
		var codeFail=function(code,msg){
			try{//跨域的优先检测一下
				window.top.a;
			}catch(e){
				failCall($T("Nclz::无权录音(跨域，请尝试给iframe添加麦克风访问策略，如{1})",0,'allow="camera;microphone"'));
				return;
			};
			
			if(codeErr1(1,code)){
				if(/Found/i.test(code)){//可能是非安全环境导致的没有设备
					failCall(msg+$T("jBa9::，无可用麦克风"));
				}else{
					failCall(msg);
				};
			};
		};
		var codeErr1=function(call,code){ //排除几个明确原因的错误
			if(/Permission|Allow/i.test(code)){
				if(call) failCall($T("gyO5::用户拒绝了录音权限"),true);
			}else if(window.isSecureContext===false){
				if(call) failCall($T("oWNo::浏览器禁止不安全页面录音，可开启https解决"));
			}else{
				return 1;
			};
		};
		
		
		//如果已打开并且有效就不要再打开了
		if(Recorder.IsOpen()){
			ok();
			return;
		};
		if(!Recorder.Support()){
			codeFail("",$T("COxc::此浏览器不支持录音"));
			return;
		};
		getCtx();
		
		//请求权限，如果从未授权，一般浏览器会弹出权限请求弹框
		var f1=function(stream){ //请求成功回调
			//https://github.com/xiangyuecn/Recorder/issues/14 获取到的track.readyState!="live"，刚刚回调时可能是正常的，但过一下可能就被关掉了，原因不明。延迟一下保证真异步。对正常浏览器不影响
			setTimeout(function(){
				stream._call={};
				var oldStream=Recorder.Stream;
				if(oldStream){
					Disconnect(); //直接断开已存在的，旧的Connect未完成会自动终止
					stream._call=oldStream._call;
				};
				Recorder.Stream=stream;
				stream._c=ctx;
				stream._RC=set.runningContext;
				if(lockFail())return;
				
				if(Recorder.IsOpen()){
					if(oldStream)This.CLog($T("upb8::发现同时多次调用open"),1);
					
					Connect(streamStore);
					ok(); //只连接，因为AudioContext不一定在运行，无法知道是否有数据回调
				}else{
					failCall($T("Q1GA::录音功能无效：无音频流"));
				};
			},100);
		};
		var f2=function(e){ //请求失败回调
			var code=e.name||e.message||e.code+":"+e;
			var tryMsg="";
			if(callUmCount==1 && codeErr1(0,code)){ 
				tryMsg=$T("KxE2::，将尝试禁用回声消除后重试");
			}
			var msg1=$T("xEQR::请求录音权限错误"),msg2=$T("bDOG::无法录音：");
			This.CLog(msg1+tryMsg+"|"+e,(tryMsg||f2_e)?3:1,e);
			
			if(tryMsg){//重试
				f2_c=code; f2_e=e; //重试如果还出错 返回第一个错误
				callUserMedia(1);
			}else if(f2_e){
				This.CLog(msg1+"|"+f2_e,1,f2_e);
				codeFail(f2_c,msg2+f2_e);
			}else{
				codeFail(code,msg2+e);
			};
		};
		
		var callUmCount=0,f2_c,f2_e;
		var callUserMedia=function(retry){
			callUmCount++;
			var atsTxt="audioTrackSet";
			var t_AGC="autoGainControl",t_AEC="echoCancellation",t_ANS="noiseSuppression";
			var atsTxtJs=atsTxt+":{"+t_AEC+","+t_ANS+","+t_AGC+"}";
			var trackSet=JSON.parse(ToJson(set[atsTxt]||true)); //true 跟 {} 兼容性？
			This.CLog("open... "+callUmCount+" "+atsTxt+":"+ToJson(trackSet));
			
			if(retry){ //回声消除有些浏览器可能导致无法打开录音，尝试明确禁用来保证能最基础的录
				if(typeof(trackSet)!="object")trackSet={}; //默认true
				trackSet[t_AGC]=false;
				trackSet[t_AEC]=false;
				trackSet[t_ANS]=false;
			};
			//这里指明采样率，虽然可以解决手机上MediaRecorder采样率16k的问题，是回声消除导致的只能获取到16k的流，禁用回声消除可恢复48k。(issues#230)而且会导致乱用音频输入设备，MediaStreamTrack的applyConstraints也无法修改采样率
			//trackSet[sampleRateTxt]=ctx[sampleRateTxt];
			if(trackSet[sampleRateTxt]){
				This.CLog($T("IjL3::注意：已配置{1}参数，可能会出现浏览器不能正确选用麦克风、移动端无法启用回声消除等现象",0,atsTxt+"."+sampleRateTxt),3);
			};
			
			var mSet={audio:trackSet, video:set.videoTrackSet||false};
			try{
				var pro=Recorder.Scope[getUserMediaTxt](mSet,f1,f2);
			}catch(e){//不能设置trackSet就算了
				This.CLog(getUserMediaTxt,3,e);
				mSet={audio:true, video:false};
				pro=Recorder.Scope[getUserMediaTxt](mSet,f1,f2);
			};
			This.CLog(getUserMediaTxt+"("+ToJson(mSet)+") "+CtxState(ctx)
				+$T("RiWe::，未配置 {1} 时浏览器可能会自动启用回声消除，移动端未禁用回声消除时可能会降低系统播放音量（关闭录音后可恢复）和仅提供16k采样率的音频流（不需要回声消除时可明确配置成禁用来获得48k高音质的流），请参阅文档中{2}配置",0,atsTxtJs,atsTxt)
				+"("+GitUrl+") LM:"+LM+" UA:"+navigator.userAgent);
			if(pro&&pro.then){
				pro.then(f1)[CatchTxt](f2); //fix 关键字，保证catch压缩时保持字符串形式
			};
		};
		callUserMedia();
	}
	//关闭释放录音资源
	,close:function(call){
		call=call||NOOP;
		
		var This=this,streamStore=This._streamStore();
		This._stop();
		var sTag=" stream:"+This._streamTag;
		
		var Lock=streamStore.Sync;
		This._O=0;
		if(This._O_!=Lock.O){
			//唯一资源Stream的控制权已交给新对象，这里不能关闭。此处在每次都弹权限的浏览器内可能存在泄漏，新对象被拒绝权限可能不会调用close，忽略这种不处理
			This.CLog($T("hWVz::close被忽略（因为同时open了多个rec，只有最后一个会真正close）")+sTag,3);
			call();
			return;
		};
		Lock.C++;//获得控制权
		
		Disconnect(streamStore);
		
		This.CLog("close,"+sTag);
		call();
	}
	
	
	
	
	
	/*模拟一段录音数据，后面可以调用stop进行编码，需提供pcm数据[1,2,3...]，pcm的采样率*/
	,mock:function(pcmData,pcmSampleRate){
		var This=this;
		This._stop();//清理掉已有的资源
		
		This.isMock=1;
		This.mockEnvInfo=null;
		This.buffers=[pcmData];
		This.recSize=pcmData.length;
		This._setSrcSR(pcmSampleRate);
		This._streamTag="mock";
		return This;
	}
	,_setSrcSR:function(sampleRate){
		var This=this,set=This.set;
		var setSr=set[sampleRateTxt];
		if(setSr>sampleRate){
			set[sampleRateTxt]=sampleRate;
		}else{ setSr=0 }
		This[srcSampleRateTxt]=sampleRate;
		This.CLog(srcSampleRateTxt+": "+sampleRate+" set."+sampleRateTxt+": "+set[sampleRateTxt]+(setSr?" "+$T("UHvm::忽略")+": "+setSr:""), setSr?3:0);
	}
	,envCheck:function(envInfo){//平台环境下的可用性检查，任何时候都可以调用检查，返回errMsg:""正常，"失败原因"
		//envInfo={envName:"H5",canProcess:true}
		var errMsg,This=this,set=This.set;
		
		//检测CPU的数字字节序，TypedArray字节序是个迷，直接拒绝罕见的大端模式，因为找不到这种CPU进行测试
		var tag="CPU_BE";
		if(!errMsg && !Recorder[tag] && typeof Int8Array=="function" && !new Int8Array(new Int32Array([1]).buffer)[0]){
			Traffic(tag); //如果开启了流量统计，这里将发送一个图片请求
			errMsg=$T("Essp::不支持{1}架构",0,tag);
		};
		
		//编码器检查环境下配置是否可用
		if(!errMsg){
			var type=set.type,hasFn=This[type+"_envCheck"];
			if(set.takeoffEncodeChunk){//需要实时编码返回数据，此时需要检查环境是否有实时特性、和是否可实时编码
				if(!hasFn){
					errMsg=$T("2XBl::{1}类型不支持设置takeoffEncodeChunk",0,type)+(This[type]?"":$T("LG7e::(未加载编码器)"));
				}else if(!envInfo.canProcess){
					errMsg=$T("7uMV::{1}环境不支持实时处理",0,envInfo.envName);
				};
			};
			
			if(!errMsg && hasFn){//编码器已实现环境检查
				errMsg=This[type+"_envCheck"](envInfo,set);
			};
		};
		
		return errMsg||"";
	}
	,envStart:function(mockEnvInfo,sampleRate){//平台环境相关的start调用
		var This=this,set=This.set;
		This.isMock=mockEnvInfo?1:0;//非H5环境需要启用mock，并提供envCheck需要的环境信息
		This.mockEnvInfo=mockEnvInfo;
		This.buffers=[];//数据缓冲
		This.recSize=0;//数据大小
		if(mockEnvInfo){
			This._streamTag="env$"+mockEnvInfo.envName;
		};
		
		This.state=1;//运行状态，0未录音 1录音中 2暂停 3等待ctx激活
		This.envInLast=0;//envIn接收到最后录音内容的时间
		This.envInFirst=0;//envIn接收到的首个录音内容的录制时间
		This.envInFix=0;//补偿的总时间
		This.envInFixTs=[];//补偿计数列表
		
		//engineCtx需要提前确定最终的采样率
		This._setSrcSR(sampleRate);
		
		This.engineCtx=0;
		//此类型有边录边转码(Worker)支持
		if(This[set.type+"_start"]){
			var engineCtx=This.engineCtx=This[set.type+"_start"](set);
			if(engineCtx){
				engineCtx.pcmDatas=[];
				engineCtx.pcmSize=0;
			};
		};
	}
	,envResume:function(){//和平台环境无关的恢复录音
		//重新开始计数
		this.envInFixTs=[];
	}
	,envIn:function(pcm,sum){//和平台环境无关的pcm[Int16]输入
		var This=this,set=This.set,engineCtx=This.engineCtx;
		if(This.state!=1){
			if(!This.state)This.CLog("envIn at state=0",3);
			return;
		};
		var bufferSampleRate=This[srcSampleRateTxt];
		var size=pcm.length;
		var powerLevel=Recorder.PowerLevel(sum,size);
		
		var buffers=This.buffers;
		var bufferFirstIdx=buffers.length;//之前的buffer都是经过onProcess处理好的，不允许再修改
		buffers.push(pcm);
		
		//有engineCtx时会被覆盖，这里保存一份
		var buffersThis=buffers;
		var bufferFirstIdxThis=bufferFirstIdx;
		
		//卡顿丢失补偿：因为设备很卡的时候导致H5接收到的数据量不够造成播放时候变速，结果比实际的时长要短，此处保证了不会变短，但不能修复丢失的音频数据造成音质变差。当前算法采用输入时间侦测下一帧是否需要添加补偿帧，需要(6次输入||超过1秒)以上才会开始侦测，如果滑动窗口内丢失超过1/3就会进行补偿
		var now=Date.now();
		var pcmTime=Math.round(size/bufferSampleRate*1000);
		This.envInLast=now;
		if(This.buffers.length==1){//记下首个录音数据的录制时间
			This.envInFirst=now-pcmTime;
		};
		var envInFixTs=This.envInFixTs;
		envInFixTs.splice(0,0,{t:now,d:pcmTime});
		//保留3秒的计数滑动窗口，另外超过3秒的停顿不补偿
		var tsInStart=now,tsPcm=0;
		for(var i=0;i<envInFixTs.length;i++){
			var o=envInFixTs[i];
			if(now-o.t>3000){
				envInFixTs.length=i;
				break;
			};
			tsInStart=o.t;
			tsPcm+=o.d;
		};
		//达到需要的数据量，开始侦测是否需要补偿
		var tsInPrev=envInFixTs[1];
		var tsIn=now-tsInStart;
		var lost=tsIn-tsPcm;
		if( lost>tsIn/3 && (tsInPrev&&tsIn>1000 || envInFixTs.length>=6) ){
			//丢失过多，开始执行补偿
			var addTime=now-tsInPrev.t-pcmTime;//距离上次输入丢失这么多ms
			if(addTime>pcmTime/5){//丢失超过本帧的1/5
				var fixOpen=!set.disableEnvInFix;
				This.CLog("["+now+"]"+i18n.get(fixOpen?$T("4Kfd::补偿{1}ms",1):$T("bM5i::未补偿{1}ms",1),[addTime]),3);
				This.envInFix+=addTime;
				
				//用静默进行补偿
				if(fixOpen){
					var addPcm=new Int16Array(addTime*bufferSampleRate/1000);
					size+=addPcm.length;
					buffers.push(addPcm);
				};
			};
		};
		
		
		var sizeOld=This.recSize,addSize=size;
		var bufferSize=sizeOld+addSize;
		This.recSize=bufferSize;//此值在onProcess后需要修正，可能新数据被修改
		
		
		//此类型有边录边转码(Worker)支持，开启实时转码
		if(engineCtx){
			//转换成set的采样率
			var chunkInfo=Recorder.SampleData(buffers,bufferSampleRate,set[sampleRateTxt],engineCtx.chunkInfo);
			engineCtx.chunkInfo=chunkInfo;
			
			sizeOld=engineCtx.pcmSize;
			addSize=chunkInfo.data.length;
			bufferSize=sizeOld+addSize;
			engineCtx.pcmSize=bufferSize;//此值在onProcess后需要修正，可能新数据被修改
			
			buffers=engineCtx.pcmDatas;
			bufferFirstIdx=buffers.length;
			buffers.push(chunkInfo.data);
			bufferSampleRate=chunkInfo[sampleRateTxt];
		};
		
		var duration=Math.round(bufferSize/bufferSampleRate*1000);
		var bufferNextIdx=buffers.length;
		var bufferNextIdxThis=buffersThis.length;
		
		//允许异步处理buffer数据
		var asyncEnd=function(){
			//重新计算size，异步的早已减去添加的，同步的需去掉本次添加的然后重新计算
			var num=asyncBegin?0:-addSize;
			var hasClear=buffers[0]==null;
			for(var i=bufferFirstIdx;i<bufferNextIdx;i++){
				var buffer=buffers[i];
				if(buffer==null){//已被主动释放内存，比如长时间实时传输录音时
					hasClear=1;
				}else{
					num+=buffer.length;
					
					//推入后台边录边转码
					if(engineCtx&&buffer.length){
						This[set.type+"_encode"](engineCtx,buffer);
					};
				};
			};
			
			//同步清理This.buffers，不管buffers到底清了多少个，buffersThis是使用不到的进行全清
			if(hasClear && engineCtx){
				var i=bufferFirstIdxThis;
				if(buffersThis[0]){
					i=0;
				};
				for(;i<bufferNextIdxThis;i++){
					buffersThis[i]=null;
				};
			};
			
			//统计修改后的size，如果异步发生clear要原样加回来，同步的无需操作
			if(hasClear){
				num=asyncBegin?addSize:0;
				
				buffers[0]=null;//彻底被清理
			};
			if(engineCtx){
				engineCtx.pcmSize+=num;
			}else{
				This.recSize+=num;
			};
		};
		//实时回调处理数据，允许修改或替换上次回调以来新增的数据 ，但是不允许修改已处理过的，不允许增删第一维数组 ，允许将第二维数组任意修改替换成空数组也可以
		var asyncBegin=0,procTxt="rec.set.onProcess";
		try{
			asyncBegin=set.onProcess(buffers,powerLevel,duration,bufferSampleRate,bufferFirstIdx,asyncEnd);
			asyncBegin=asyncBegin===true;
		}catch(e){
			//此错误显示不要用CLog，这样控制台内相同内容不会重复打印
			console.error(procTxt+$T("gFUF::回调出错是不允许的，需保证不会抛异常"),e);
		};
		
		var slowT=Date.now()-now;
		if(slowT>10 && This.envInFirst-now>1000){ //1秒后开始onProcess性能监测
			This.CLog(procTxt+$T("2ghS::低性能，耗时{1}ms",0,slowT),3);
		};
		
		if(asyncBegin){
			//开启了异步模式，onProcess已接管buffers新数据，立即清空，避免出现未处理的数据
			var hasClear=0;
			for(var i=bufferFirstIdx;i<bufferNextIdx;i++){
				if(buffers[i]==null){//已被主动释放内存，比如长时间实时传输录音时 ，但又要开启异步模式，此种情况是非法的
					hasClear=1;
				}else{
					buffers[i]=new Int16Array(0);
				};
			};
			
			if(hasClear){
				This.CLog($T("ufqH::未进入异步前不能清除buffers"),3);
			}else{
				//还原size，异步结束后再统计仅修改后的size，如果发生clear要原样加回来
				if(engineCtx){
					engineCtx.pcmSize-=addSize;
				}else{
					This.recSize-=addSize;
				};
			};
		}else{
			asyncEnd();
		};
	}
	
	
	
	
	//开始录音，需先调用open；只要open成功时，调用此方法是安全的，如果未open强行调用导致的内部错误将不会有任何提示，stop时自然能得到错误；注意：open和start至少有一个应当在用户操作（触摸、点击等）下进行调用，原因参考runningContext配置
	,start:function(){
		var This=this;
		
		var isOpen=1;
		if(This.set.sourceStream){//直接提供了流，仅判断是否调用了open
			if(!This.Stream){
				isOpen=0;
			}
		}else if(!Recorder.IsOpen()){//监测全局麦克风是否打开并且有效
			isOpen=0;
		};
		if(!isOpen){
			This.CLog($T("6WmN::start失败：未open"),1);
			return;
		};
		var ctx=This._streamCtx();
		This.CLog($T("kLDN::start 开始录音，")+CtxState(ctx)+" stream:"+This._streamTag);
		
		This._stop();
		This.envStart(null, ctx[sampleRateTxt]);
		This.state=3;//0未录音 1录音中 2暂停 3等待ctx激活
		
		//检查open过程中stop是否已经调用过
		if(This._SO&&This._SO+1!=This._S){//上面调用过一次 _stop
			//open未完成就调用了stop，此种情况终止start。也应尽量避免出现此情况
			This.CLog($T("Bp2y::start被中断"),3);
			return;
		};
		This._SO=0;
		
		var end=function(){
			if(This.state==3){
				This.state=1;
				This.resume();
			}
		};
		var tag="AudioContext resume: ";
		
		//如果有数据回调，就不等待ctx resume
		var stream=This._streamGet();
		stream._call[This.id]=function(){
			This.CLog(tag+ctx.state+'|stream ok');
			end();
		};
		ResumeCtx(ctx,function(runC){
			runC&&This.CLog(tag+"wait...");
			return This.state==3;
		},function(runC){
			runC&&This.CLog(tag+ctx.state);
			end();
		},function(err){ //比较少见，可能对录音没有影响
			This.CLog(tag+ctx.state+$T("upkE::，可能无法录音：")+err,1);
			end();
		});
	}
	
	
	
	/*暂停录音*/
	,pause:function(){
		var This=this,stream=This._streamGet();
		if(This.state){
			This.state=2;
			This.CLog("pause");
			if(stream) delete stream._call[This.id];
		};
	}
	/*恢复录音*/
	,resume:function(){
		var This=this,stream=This._streamGet();
		var tag="resume",tag3=tag+"(wait ctx)";
		if(This.state==3){ //start还在等ctx恢复
			This.CLog(tag3);
		}else if(This.state){
			This.state=1;
			This.CLog(tag);
			This.envResume();
			
			if(stream){
				stream._call[This.id]=function(pcm,sum){
					if(This.state==1){
						This.envIn(pcm,sum);
					};
				};
				ConnAlive(stream);//AudioWorklet只会在ctx激活后运行
			};
			
			var ctx=This._streamCtx();
			if(ctx){ //AudioContext如果被暂停，尽量恢复
				ResumeCtx(ctx,function(runC){
					runC&&This.CLog(tag3+"...");
					return This.state==1;
				},function(runC){
					runC&&This.CLog(tag3+ctx.state);
					ConnAlive(stream);
				},function(err){
					This.CLog(tag3+ctx.state+"[err]"+err,1);
				});
			};
		};
	}
	
	
	
	
	,_stop:function(keepEngine){
		var This=this,set=This.set;
		if(!This.isMock){
			This._S++;
		};
		if(This.state){
			This.pause();
			This.state=0;
		};
		if(!keepEngine && This[set.type+"_stop"]){
			This[set.type+"_stop"](This.engineCtx);
			This.engineCtx=0;
		};
	}
	/*
	结束录音并返回录音数据blob对象
		True(blob,duration,mime)
			blob：录音数据audio/mp3|wav格式；默认是Blob对象，可设置rec.dataType="arraybuffer"改成ArrayBuffer
			duration：录音时长，单位毫秒
			mime："auido/mp3" blob数据的类型，方便ArrayBuffer时区分类型
		False(msg)
		autoClose:false 可选，是否自动调用close，默认为false
	*/
	,stop:function(True,False,autoClose){
		var This=this,set=This.set,t1;
		var envInMS=This.envInLast-This.envInFirst, envInLen=envInMS&&This.buffers.length; //可能未start
		This.CLog($T("Xq4s::stop 和start时差:")
			+(envInMS?envInMS+"ms "+$T("3CQP::补偿:")+This.envInFix+"ms"
				+" envIn:"+envInLen+" fps:"+(envInLen/envInMS*1000).toFixed(1)
			:"-")+" stream:"+This._streamTag+" ("+GitUrl+") LM:"+LM);
		
		var end=function(){
			This._stop();//彻底关掉engineCtx
			if(autoClose){
				This.close();
			};
		};
		var err=function(msg){
			This.CLog($T("u8JG::结束录音失败：")+msg,1);
			False&&False(msg);
			end();
		};
		var ok=function(blob,mime,duration){
			var tBlob="blob",tABuf="arraybuffer",tDT="dataType",tDDT="DefaultDataType";
			var dType=This[tDT]||Recorder[tDDT]||tBlob,dTag=tDT+"="+dType;
			var isAB=blob instanceof ArrayBuffer,dErr=0;
			var dLen=isAB?blob.byteLength:blob.size;
			if(dType==tABuf){
				if(!isAB) dErr=1;
			}else if(dType==tBlob){
				if(typeof Blob!="function"){
					dErr=$T.G("NonBrowser-1",[dTag])+$T("1skY::，请设置{1}",0,RecTxt+"."+tDDT+'="'+tABuf+'"');
				}else{
					if(isAB) blob=new Blob([blob],{type:mime});
					if(!(blob instanceof Blob)) dErr=1;
					mime=blob.type||mime;
				}
			}else{
				dErr=$T.G("NotSupport-1",[dTag]);
			};
			
			This.CLog($T("Wv7l::结束录音 编码花{1}ms 音频时长{2}ms 文件大小{3}b",0,Date.now()-t1,duration,dLen)+" "+dTag+","+mime);
			if(dErr){
				err(dErr!=1?dErr:$T("Vkbd::{1}编码器返回的不是{2}",0,set.type,dType)+", "+dTag);
				return;
			};
			if(set.takeoffEncodeChunk){//接管了输出，此时blob长度为0
				This.CLog($T("QWnr::启用takeoffEncodeChunk后stop返回的blob长度为0不提供音频数据"),3);
			}else if(dLen<Math.max(50,duration/5)){//1秒小于0.2k？
				err($T("Sz2H::生成的{1}无效",0,set.type));
				return;
			};
			
			True&&True(blob,duration,mime);
			end();
		};
		if(!This.isMock){
			var isCtxWait=This.state==3;
			if(!This.state || isCtxWait){
				err($T("wf9t::未开始录音")+(isCtxWait?$T("Dl2c::，开始录音前无用户交互导致AudioContext未运行"):""));
				return;
			};
		};
		This._stop(true); //将录音状态改成未录音
		var size=This.recSize;
		if(!size){
			err($T("Ltz3::未采集到录音"));
			return;
		};
		if(!This[set.type]){
			err($T("xGuI::未加载{1}编码器，请尝试到{2}的src/engine内找到{1}的编码器并加载",0,set.type,RecTxt));
			return;
		};
		
		//环境配置检查，此处仅针对mock调用，因为open已经检查过了
		if(This.isMock){
			var checkMsg=This.envCheck(This.mockEnvInfo||{envName:"mock",canProcess:false});//没有提供环境信息的mock时没有onProcess回调
			if(checkMsg){
				err($T("AxOH::录音错误：")+checkMsg);
				return;
			};
		};
		
		//此类型有边录边转码(Worker)支持
		var engineCtx=This.engineCtx;
		if(This[set.type+"_complete"]&&engineCtx){
			var duration=Math.round(engineCtx.pcmSize/set[sampleRateTxt]*1000);//采用后的数据长度和buffers的长度可能微小的不一致，是采样率连续转换的精度问题
			
			t1=Date.now();
			This[set.type+"_complete"](engineCtx,function(blob,mime){
				ok(blob,mime,duration);
			},err);
			return;
		};
		
		//标准UI线程转码，调整采样率
		t1=Date.now();
		if(!This.buffers[0]){
			err($T("xkKd::音频buffers被释放"));
			return;
		};
		var chunk=Recorder.SampleData(This.buffers,This[srcSampleRateTxt],set[sampleRateTxt]);
		
		set[sampleRateTxt]=chunk[sampleRateTxt];
		var res=chunk.data;
		var duration=Math.round(res.length/set[sampleRateTxt]*1000);
		
		This.CLog($T("CxeT::采样:{1} 花:{2}ms",0,size+"->"+res.length,Date.now()-t1));
		
		setTimeout(function(){
			t1=Date.now();
			This[set.type](res,function(blob,mime){
				ok(blob,mime,duration);
			},function(msg){
				err(msg);
			});
		});
	}

};





//=======从WebM字节流中提取pcm数据，提取成功返回Float32Array，失败返回null||-1=====
var WebM_Extract=function(inBytes, scope){
	if(!scope.pos){
		scope.pos=[0]; scope.tracks={}; scope.bytes=[];
	};
	var tracks=scope.tracks, position=[scope.pos[0]];
	var endPos=function(){ scope.pos[0]=position[0] };
	
	var sBL=scope.bytes.length;
	var bytes=new Uint8Array(sBL+inBytes.length);
	bytes.set(scope.bytes); bytes.set(inBytes,sBL);
	scope.bytes=bytes;
	
	//先读取文件头和Track信息
	if(!scope._ht){
		readMatroskaVInt(bytes, position);//EBML Header
		readMatroskaBlock(bytes, position);//跳过EBML Header内容
		if(!BytesEq(readMatroskaVInt(bytes, position), [0x18,0x53,0x80,0x67])){
			return;//未识别到Segment
		}
		readMatroskaVInt(bytes, position);//跳过Segment长度值
		while(position[0]<bytes.length){
			var eid0=readMatroskaVInt(bytes, position);
			var bytes0=readMatroskaBlock(bytes, position);
			var pos0=[0],audioIdx=0;
			if(!bytes0)return;//数据不全，等待缓冲
			//Track完整数据，循环读取TrackEntry
			if(BytesEq(eid0, [0x16,0x54,0xAE,0x6B])){
				while(pos0[0]<bytes0.length){
					var eid1=readMatroskaVInt(bytes0, pos0);
					var bytes1=readMatroskaBlock(bytes0, pos0);
					var pos1=[0],track={channels:0,sampleRate:0};
					if(BytesEq(eid1, [0xAE])){//TrackEntry
						while(pos1[0]<bytes1.length){
							var eid2=readMatroskaVInt(bytes1, pos1);
							var bytes2=readMatroskaBlock(bytes1, pos1);
							var pos2=[0];
							if(BytesEq(eid2, [0xD7])){//Track Number
								var val=BytesInt(bytes2);
								track.number=val;
								tracks[val]=track;
							}else if(BytesEq(eid2, [0x83])){//Track Type
								var val=BytesInt(bytes2);
								if(val==1) track.type="video";
								else if(val==2) {
									track.type="audio";
									if(!audioIdx) scope.track0=track;
									track.idx=audioIdx++;
								}else track.type="Type-"+val;
							}else if(BytesEq(eid2, [0x86])){//Track Codec
								var str="";
								for(var i=0;i<bytes2.length;i++){
									str+=String.fromCharCode(bytes2[i]);
								}
								track.codec=str;
							}else if(BytesEq(eid2, [0xE1])){
								while(pos2[0]<bytes2.length){//循环读取 Audio 属性
									var eid3=readMatroskaVInt(bytes2, pos2);
									var bytes3=readMatroskaBlock(bytes2, pos2);
									//采样率、位数、声道数
									if(BytesEq(eid3, [0xB5])){
										var val=0,arr=new Uint8Array(bytes3.reverse()).buffer;
										if(bytes3.length==4) val=new Float32Array(arr)[0];
										else if(bytes3.length==8) val=new Float64Array(arr)[0];
										else CLog("WebM Track !Float",1,bytes3);
										track[sampleRateTxt]=Math.round(val);
									}else if(BytesEq(eid3, [0x62,0x64])) track.bitDepth=BytesInt(bytes3);
									else if(BytesEq(eid3, [0x9F])) track.channels=BytesInt(bytes3);
								}
							}
						}
					}
				};
				scope._ht=1;
				CLog("WebM Tracks",tracks);
				endPos();
				break;
			}
		}
	}
	
	//校验音频参数信息，如果不符合代码要求，统统拒绝处理
	var track0=scope.track0;
	if(!track0)return;
	var trackSR=track0[sampleRateTxt]; scope.webmSR=trackSR;
	if(track0.bitDepth==16 && /FLOAT/i.test(track0.codec)){
		track0.bitDepth=32; //chrome v66 实际为浮点数
		CLog("WebM 16->32 bit",3);
	}
	if(trackSR<8000 || track0.bitDepth!=32 || track0.channels<1 || !/(\b|_)PCM\b/i.test(track0.codec)){
		scope.bytes=[];//格式非预期 无法处理，清空缓冲数据
		if(!scope.bad)CLog("WebM Track Unexpected",3,scope);
		scope.bad=1;
		return -1;
	}
	
	//循环读取Cluster内的SimpleBlock
	var datas=[],dataLen=0;
	while(position[0]<bytes.length){
		var eid1=readMatroskaVInt(bytes, position);
		var bytes1=readMatroskaBlock(bytes, position);
		if(!bytes1)break;//数据不全，等待缓冲
		if(BytesEq(eid1, [0xA3])){//SimpleBlock完整数据
			var trackNo=bytes1[0]&0xf;
			var track=tracks[trackNo];
			if(!track){//不可能没有，数据出错？
				CLog("WebM !Track"+trackNo,1,tracks);
				return -1; //可能无法继续
			}else if(track.idx===0){
				var u8arr=new Uint8Array(bytes1.length-4);
				for(var i=4;i<bytes1.length;i++){
					u8arr[i-4]=bytes1[i];
				}
				datas.push(u8arr); dataLen+=u8arr.length;
			}
		}
		endPos();
	}
	
	if(dataLen){
		var more=new Uint8Array(bytes.length-scope.pos[0]);
		more.set(bytes.subarray(scope.pos[0]));
		scope.bytes=more; //清理已读取了的缓冲数据
		scope.pos[0]=0;
		
		var u8arr=new Uint8Array(dataLen); //已获取的音频数据
		for(var i=0,i2=0;i<datas.length;i++){
			u8arr.set(datas[i],i2);
			i2+=datas[i].length;
		}
		var arr=new Float32Array(u8arr.buffer);
		
		if(track0.channels>1){//多声道，提取一个声道
			var arr2=[];
			for(var i=0;i<arr.length;){
				arr2.push(arr[i]);
				i+=track0.channels;
			}
			arr=new Float32Array(arr2);
		};
		return arr;
	}
};
//两个字节数组内容是否相同
var BytesEq=function(bytes1,bytes2){
	if(!bytes1 || bytes1.length!=bytes2.length) return false;
	if(bytes1.length==1) return bytes1[0]==bytes2[0];
	for(var i=0;i<bytes1.length;i++){
		if(bytes1[i]!=bytes2[i]) return false;
	}
	return true;
};
//字节数组BE转成int数字
var BytesInt=function(bytes){
	var s="";//0-8字节，js位运算只支持4字节
	for(var i=0;i<bytes.length;i++){var n=bytes[i];s+=(n<16?"0":"")+n.toString(16)};
	return parseInt(s,16)||0;
};
//读取一个可变长数值字节数组
var readMatroskaVInt=function(arr,pos,trim){
	var i=pos[0];
	if(i>=arr.length)return;
	var b0=arr[i],b2=("0000000"+b0.toString(2)).substr(-8);
	var m=/^(0*1)(\d*)$/.exec(b2);
	if(!m)return;
	var len=m[1].length, val=[];
	if(i+len>arr.length)return;
	for(var i2=0;i2<len;i2++){ val[i2]=arr[i]; i++; }
	if(trim) val[0]=parseInt(m[2]||'0',2);
	pos[0]=i;
	return val;
};
//读取一个自带长度的内容字节数组
var readMatroskaBlock=function(arr,pos){
	var lenVal=readMatroskaVInt(arr,pos,1);
	if(!lenVal)return;
	var len=BytesInt(lenVal);
	var i=pos[0], val=[];
	if(len<0x7FFFFFFF){ //超大值代表没有长度
		if(i+len>arr.length)return;
		for(var i2=0;i2<len;i2++){ val[i2]=arr[i]; i++; }
	}
	pos[0]=i;
	return val;
};
//=====End WebM读取=====


//=====i18n 简版国际化多语言支持=====
var i18n=Recorder.i18n={
	lang: "zh-CN" //默认中文
	,alias:{"zh-CN":"zh","en-US":"en"} //别名配置，映射到一个语言实例
	,locales:{} //语言实例：zh:{key:"text"}
	,data:{} //各种数据，desc$xx：语言描述，rtl$xx：文本方向是否从右到左 rtl$zh:false rtl$ar:true
	//添加语言文本内容，set={lang:"",overwrite:true}，texts=["key:text{1}",...]
	,put:function(set,texts){
		var tag=RecTxt+".i18n.put: ";
		var overwrite=set.overwrite; overwrite=overwrite==null||overwrite;
		var lang=set.lang; lang=i18n.alias[lang]||lang;
		if(!lang)throw new Error(tag+"set.lang?");
		var locale=i18n.locales[lang];
		if(!locale){ locale={}; i18n.locales[lang]=locale };
		var exp=/^([\w\-]+):/,m;
		for(var i=0;i<texts.length;i++){
			var v=texts[i]; m=exp.exec(v);
			if(!m){ CLog(tag+"'key:'? "+v,3,set); continue }
			var key=m[1],v=v.substr(key.length+1);
			if(!overwrite && locale[key]) continue;
			locale[key]=v;
		}
	}
	//获取key对应的文本，如果没有对应文本，将返回en的，en的也没有将返回zh的
	,get:function(/*key,args,lang*/){
		return i18n.v_G.apply(null,arguments);
	}, v_G:function(key,args,lang){ //全局可重写get
		args=args||[];
		lang=lang||i18n.lang; lang=i18n.alias[lang]||lang;
		var locale=i18n.locales[lang];
		var val=locale&&locale[key]||"";
		if(!val&&lang!="zh"){
			if(lang=="en")return i18n.v_G(key,args,"zh");
			return i18n.v_G(key,args,"en");
		}
		i18n.lastLang=lang;
		if(val=="=Empty")return "";
		return val.replace(/\{(\d+)(\!?)\}/g,function(v,a,b){
			a=+a||0; v=args[a-1];
			if(a<1 || a>args.length){ v="{?}"; CLog("i18n["+key+"] no {"+a+"}: "+val,3) }
			return b?"":v;
		});
	}
	/**返回一个国际化文本，返回的文本取决于i18n.lang。
		调用参数：T("key:[lang]:中文{1}","[lang]:英文{1}",...,0,"args1","args2")，除了key:，其他都是可选的，文本如果在语言实例中不存在会push进去，第一个文本无lang时默认zh，第二个无lang时默认en，文本中用{1-n}来插入args
		第一个args前面这个参数必须是0；也可以不提供args，这个参数填args的数量，此时不返回文本，只返回key，再用i18n.get提供参数获取文本
		本函数调用，第一个文本需中文，调用尽量简单，不要换行，方便后续自动提取翻译列表
		args如果旧的参数位置发生了变更，应当使用新的key，让旧的翻译失效，增加args无需更换key
		key的生成使用随机字符串，不同源码里面可以搞个不同前缀:
			s="";L=4; for(var i=0,n;i<L;i++){ n=~~(Math.random()*62);s+=n<10?n:String.fromCharCode(n<36?55+n:61+n); }; s
	**/
	,$T:function(){
		return i18n.v_T.apply(null,arguments);
	} ,v_T:function(){ //全局可重写$T
		var a=arguments,key="",args=[],isArgs=0,tag=RecTxt+".i18n.$T:";
		var exp=/^([\w\-]*):/,m;
		for(var i=0;i<a.length;i++){
			var v=a[i];
			if(i==0){
				m=exp.exec(v); key=m&&m[1];
				if(!key)throw new Error(tag+"0 'key:'?");
				v=v.substr(key.length+1);
			}
			if(isArgs===-1) args.push(v);
			else if(isArgs) throw new Error(tag+" bad args");
			else if(v===0) isArgs=-1;
			else if(IsNum(v)){
				if(v<1) throw new Error(tag+" bad args");
				isArgs=v;
			}else{
				var lang=i==1?"en":i?"":"zh";
				m=exp.exec(v); if(m){ lang=m[1]||lang; v=v.substr(m[1].length+1); }
				if(!m || !lang)throw new Error(tag+i+" 'lang:'?");
				i18n.put({lang:lang,overwrite:false},[key+":"+v]);
			}
		}
		if(!key)return "";
		if(isArgs>0)return key;
		return i18n.v_G(key,args);
	}
};
var $T=i18n.$T; $T.G=i18n.get;
//预定义文本
$T("NonBrowser-1::非浏览器环境，不支持{1}",1);
$T("IllegalArgs-1::参数错误：{1}",1);
$T("NeedImport-2::调用{1}需要先导入{2}",2);
$T("NotSupport-1::不支持：{1}",1);
//=====End i18n=====



//流量统计用1像素图片地址，设置为空将不参与统计
Recorder.TrafficImgUrl="//ia.51.la/go1?id=20469973&pvFlag=1";
var Traffic=Recorder.Traffic=function(report){
	if(!isBrowser)return;
	report=report?"/"+RecTxt+"/Report/"+report:"";
	var imgUrl=Recorder.TrafficImgUrl;
	if(imgUrl){
		var data=Recorder.Traffic;
		var m=/^(https?:..[^\/#]*\/?)[^#]*/i.exec(location.href)||[];
		var host=(m[1]||"http://file/");
		var idf=(m[0]||host)+report;
		
		if(imgUrl.indexOf("//")==0){
			//给url加上http前缀，如果是file协议下，不加前缀没法用
			if(/^https:/i.test(idf)){
				imgUrl="https:"+imgUrl;
			}else{
				imgUrl="http:"+imgUrl;
			};
		};
		if(report){
			imgUrl=imgUrl+"&cu="+encodeURIComponent(host+report);
		};
		
		if(!data[idf]){
			data[idf]=1;
			
			var img=new Image();
			img.src=imgUrl;
			CLog("Traffic Analysis Image: "+(report||RecTxt+".TrafficImgUrl="+Recorder.TrafficImgUrl));
		};
	};
};



if(WRec2){
	CLog($T("8HO5::覆盖导入{1}",0,RecTxt),1);
	WRec2.Destroy();
};
Export[RecTxt]=Recorder;

}));