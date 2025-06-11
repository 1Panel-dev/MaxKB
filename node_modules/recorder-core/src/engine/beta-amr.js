/*
amr编码器，beta版，需带上src/engine/amr-engine.js引擎使用。如果需要播放amr音频，需要额外带上wav.js引擎来调用Recorder.amr2wav把amr转成wav播放
https://github.com/xiangyuecn/Recorder

当然最佳推荐使用mp3、wav格式，代码也是优先照顾这两种格式
浏览器支持情况
https://developer.mozilla.org/en-US/docs/Web/HTML/Supported_media_formats

FFmpeg转码：
[ wav->AMR-NB] ffmpeg.exe -i test.wav -ar 8000 -ab 6.7k -ac 1 amr-6.7.amr
[ wav->AMR-NB] ffmpeg.exe -i test.wav -ar 8000 -ab 12.2k -ac 1 amr-12.2.amr
[ wav->AMR-WB] ffmpeg.exe -i test.wav -acodec libvo_amrwbenc -ar 16000 -ab 23.85k -ac 1 amr-23.85.amr
*/
(function(factory){
	var browser=typeof window=="object" && !!window.document;
	var win=browser?window:Object; //非浏览器环境，Recorder挂载在Object下面
	var rec=win.Recorder,ni=rec.i18n;
	factory(rec,ni,ni.$T,browser);
}(function(Recorder,i18n,$T,isBrowser){
"use strict";

var BitS="4.75, 5.15, 5.9, 6.7, 7.4, 7.95, 10.2, 12.2";
Recorder.prototype.enc_amr={
	stable:true,takeEC:"full"
	,getTestMsg:function(){
		return $T("b2mN::AMR-NB(NarrowBand)，采样率设置无效（只提供8000hz），比特率范围：{1}（默认12.2kbps），一帧20ms、{2}字节；浏览器一般不支持播放amr格式，可用Recorder.amr2wav()转码成wav播放",0,BitS,"Math.ceil(bitRate/8*20)+1");
	}
};

var NormalizeSet=function(set){
	var bS=set.bitRate,b=Recorder.AMR.BitRate(bS);
	var sS=set.sampleRate,s=8000;
	if(bS!=b || sS!=s) Recorder.CLog($T("tQBv::AMR Info: 和设置的不匹配{1}，已更新成{2}",0,"set:"+bS+"kbps "+sS+"hz","set:"+b+"kbps "+s+"hz"),3);
	set.bitRate=b;
	set.sampleRate=s;
};
var ImportEngineErr=function(){
	return $T.G("NeedImport-2",["beta-amr.js","src/engine/beta-amr-engine.js"]);
};
//是否支持web worker
var HasWebWorker=isBrowser && typeof Worker=="function";


/**amr转码成wav，可以直接用来播放；需同时引入src/engine/wav.js
amrBlob: amr音频文件blob对象 或 ArrayBuffer（回调也将返回ArrayBuffer）
True(wavBlob,duration,mime)
False(msg)
**/
Recorder.amr2wav=function(amrBlob,True,False){
	if(!Recorder.AMR){
		False(ImportEngineErr()); return;
	};
	if(!Recorder.prototype.wav){
		False($T.G("NeedImport-2",["amr2wav","src/engine/wav.js"]));
		return;
	};
	
	var loadOk=function(arrB,dArrB){
		var amr=new Uint8Array(arrB);
		Recorder.AMR.decode(amr,function(pcm){
			var rec=Recorder({type:"wav"});
			if(dArrB)rec.dataType="arraybuffer";
			rec.mock(pcm,8000).stop(function(wavBlob,duration,mime){
				True(wavBlob,duration,mime);
			},False);
		},False);
	};
	
	if(amrBlob instanceof ArrayBuffer){
		loadOk(amrBlob,1);
	}else{
		var reader=new FileReader();
		reader.onloadend=function(){
			loadOk(reader.result);
		};
		reader.readAsArrayBuffer(amrBlob);
	};
};


//*******标准UI线程转码支持函数************

Recorder.prototype.amr=function(res,True,False){
		var This=this,set=This.set,srcSampleRate=set.sampleRate,sampleRate=8000;
		if(!Recorder.AMR){
			False(ImportEngineErr()); return;
		};
		
		//必须先处理好采样率
		NormalizeSet(set);
		if(srcSampleRate>sampleRate){
			res=Recorder.SampleData([res],srcSampleRate,sampleRate).data;
		}else if(srcSampleRate<sampleRate){
			False($T("q12D::数据采样率低于{1}",0,sampleRate)); return;
		};
		
		//优先采用worker编码，非worker时用老方法提供兼容
		if(HasWebWorker){
			var ctx=This.amr_start(set);
			if(ctx){
				if(ctx.isW){
					This.amr_encode(ctx,res);
					This.amr_complete(ctx,True,False,1);
					return;
				}
				This.amr_stop(ctx);
			};
		};
		
		Recorder.AMR.encode(res,function(data){
			True(data.buffer,"audio/amr");
		},False,set.bitRate);
	};


//********边录边转码(Worker)支持函数，如果提供就代表可能支持，否则只支持标准转码*********

//全局共享一个Worker，后台串行执行
var amrWorker;
Recorder.BindDestroy("amrWorker",function(){
	if(amrWorker){
		Recorder.CLog("amrWorker Destroy");
		amrWorker.terminate();
		amrWorker=null;
	};
});


Recorder.prototype.amr_envCheck=function(envInfo,set){//检查环境下配置是否可用
	var errMsg="";
	//需要实时编码返回数据，此时需要检查是否可实时编码
	if(set.takeoffEncodeChunk){
		if(!newContext()){//浏览器不能创建实时编码环境
			errMsg=$T("TxjV::当前浏览器版本太低，无法实时处理");
		};
	};
	if(!errMsg && !Recorder.AMR){
		errMsg=ImportEngineErr();
	};
	return errMsg;
};
Recorder.prototype.amr_start=function(set){//如果返回null代表不支持
	return newContext(set);
};
var openList={id:0};
var newContext=function(setOrNull,_badW){
	//独立运行的函数，scope.wkScope worker.onmessage 字符串会被替换
	var run=function(e){
		var ed=e.data;
		var wk_ctxs=scope.wkScope.wk_ctxs;
		var wk_AMR=scope.wkScope.wk_AMR;
		
		var cur=wk_ctxs[ed.id];
		if(ed.action=="init"){
			wk_ctxs[ed.id]={
				takeoff:ed.takeoff
				
				,memory:new Uint8Array(500000), mOffset:0
				,encObj:wk_AMR.GetEncoder(ed.bitRate)
			};
		}else if(!cur){
			return;
		};
		var addBytes=function(buf){
			var bufLen=buf.length;
			if(cur.mOffset+bufLen>cur.memory.length){
				var tmp=new Uint8Array(cur.memory.length+Math.max(500000,bufLen));
				tmp.set(cur.memory.subarray(0, cur.mOffset));
				cur.memory=tmp;
			}
			cur.memory.set(buf,cur.mOffset);
			cur.mOffset+=bufLen;
		};
		
		switch(ed.action){
		case "stop":
			if(!cur.isCp) try{ cur.encObj.flush() }catch(e){ console.error(e) }
			cur.encObj=null;
			delete wk_ctxs[ed.id];
			break;
		case "encode":
			if(cur.isCp)break;
			try{
				var buf=cur.encObj.encode(ed.pcm);
			}catch(e){ //精简代码调用了abort
				cur.err=e;
				console.error(e);
				break;
			};
			if(!cur._h){//添加AMR头
				cur._h=1;
				var head=wk_AMR.GetHeader();
				var buf2=new Uint8Array(head.length+buf.length);
				buf2.set(head);
				buf2.set(buf,head.length);
				buf=buf2;
			}
			if(buf.length>0){
				if(cur.takeoff){
					worker.onmessage({action:"takeoff",id:ed.id,chunk:buf});
				}else{
					addBytes(buf);
				};
			};
			break;
		case "complete":
			cur.isCp=1;
			try{ cur.encObj.flush() }catch(e){ console.error(e) }; //flush没有结果，只做释放
			if(cur.err){
				worker.onmessage({action:ed.action,id:ed.id
					,err:"AMR Encoder: "+cur.err.message});
				break;
			};
			
			worker.onmessage({
				action:ed.action
				,id:ed.id
				,blob:cur.memory.buffer.slice(0,cur.mOffset)
			});
			break;
		};
	};
	
	var initOnMsg=function(isW){
		worker.onmessage=function(e){
			var data=e; if(isW)data=e.data;
			var ctx=openList[data.id];
			if(ctx){
				if(data.action=="takeoff"){
					//取走实时生成的amr数据
					ctx.set.takeoffEncodeChunk(new Uint8Array(data.chunk.buffer));
				}else{
					//complete
					ctx.call&&ctx.call(data);
					ctx.call=null;
				};
			};
		};
	};
	var initCtx=function(){
		var ctx={worker:worker,set:setOrNull};
		if(setOrNull){
			ctx.id=++openList.id;
			openList[ctx.id]=ctx;
			
			NormalizeSet(setOrNull);
			var takeoff=!!setOrNull.takeoffEncodeChunk;
			if(takeoff){
				Recorder.CLog($T("Q7p7::takeoffEncodeChunk接管AMR编码器输出的二进制数据，只有首次回调数据（首帧）包含AMR头；在合并成AMR文件时，如果没有把首帧数据包含进去，则必须在文件开头添加上AMR头：Recorder.AMR.AMR_HEADER（转成二进制），否则无法播放"),3);
			};
			
			worker.postMessage({
				action:"init"
				,id:ctx.id
				,sampleRate:setOrNull.sampleRate
				,bitRate:setOrNull.bitRate
				,takeoff:takeoff
				
				,x:new Int16Array(5)//低版本浏览器不支持序列化TypedArray
			});
		}else{
			worker.postMessage({
				x:new Int16Array(5)//低版本浏览器不支持序列化TypedArray
			});
		};
		return ctx;
	};
	var scope,worker=amrWorker;
	
	//非浏览器，不支持worker，或者开启失败，使用UI线程处理
	if(_badW || !HasWebWorker){
		Recorder.CLog($T("6o9Z::当前环境不支持Web Worker，amr实时编码器运行在主线程中"),3);
		worker={ postMessage:function(ed){ run({data:ed}); } };
		scope={wkScope:{
			wk_ctxs:{}, wk_AMR:Recorder.AMR
		}};
		initOnMsg();
		return initCtx();
	};
	
	try{
		if(!worker){
			//创建一个新Worker
			var onmsg=(run+"").replace(/[\w\$]+\.onmessage/g,"self.postMessage");
			onmsg=onmsg.replace(/[\w\$]+\.wkScope/g,"wkScope");
			var jsCode=");self.onmessage="+onmsg;
			jsCode+=";var wkScope={ wk_ctxs:{},wk_AMR:Create() }";
			
			var engineCode=Recorder.AMR.Create.toString();
			var url=(window.URL||webkitURL).createObjectURL(new Blob(["var Create=(",engineCode,jsCode], {type:"text/javascript"}));
			
			worker=new Worker(url);
			setTimeout(function(){
				(window.URL||webkitURL).revokeObjectURL(url);//必须要释放，不然每次调用内存都明显泄露内存
			},10000);//chrome 83 file协议下如果直接释放，将会使WebWorker无法启动
			initOnMsg(1);
		};
		
		var ctx=initCtx(); ctx.isW=1;
		amrWorker=worker;
		return ctx;
	}catch(e){//出错了就不要提供了
		worker&&worker.terminate();
		console.error(e);
		return newContext(setOrNull, 1);//切换到UI线程处理
	};
};
Recorder.prototype.amr_stop=function(startCtx){
	if(startCtx&&startCtx.worker){
		startCtx.worker.postMessage({
			action:"stop"
			,id:startCtx.id
		});
		startCtx.worker=null;
		delete openList[startCtx.id];
		
		//疑似泄露检测 排除id
		var opens=-1;
		for(var k in openList){
			opens++;
		};
		if(opens){
			Recorder.CLog($T("yYWs::amr worker剩{1}个未stop",0,opens),3);
		};
	};
};
Recorder.prototype.amr_encode=function(startCtx,pcm){
	if(startCtx&&startCtx.worker){
		startCtx.worker.postMessage({
			action:"encode"
			,id:startCtx.id
			,pcm:pcm
		});
	};
};
Recorder.prototype.amr_complete=function(startCtx,True,False,autoStop){
	var This=this;
	if(startCtx&&startCtx.worker){
		startCtx.call=function(data){
			if(autoStop){
				This.amr_stop(startCtx);
			};
			if(data.err){
				False(data.err);
			}else{
				True(data.blob,"audio/amr");
			};
		};
		startCtx.worker.postMessage({
			action:"complete"
			,id:startCtx.id
		});
	}else{
		False($T("jOi8::amr编码器未start"));
	};
};


}));