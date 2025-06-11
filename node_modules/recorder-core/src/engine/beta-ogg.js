/*
ogg编码器，beta版，需带上src/engine/beta-ogg-engine.js引擎使用
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

Recorder.prototype.enc_ogg={
	stable:true,takeEC:"slow"
	,getTestMsg:function(){
		return $T("O8Gn::Ogg Vorbis，比特率取值16-100kbps，采样率取值无限制");
	}
};

var ImportEngineErr=function(){
	return $T.G("NeedImport-2",["beta-ogg.js","src/engine/beta-ogg-engine.js"]);
};
//是否支持web worker
var HasWebWorker=isBrowser && typeof Worker=="function";


//*******标准UI线程转码支持函数************

Recorder.prototype.ogg=function(res,True,False){
		var This=this,set=This.set,size=res.length,bitRate=set.bitRate;
		if(!Recorder.OggVorbisEncoder){
			False(ImportEngineErr()); return;
		};
		
		//优先采用worker编码，非worker时用老方法提供兼容
		if(HasWebWorker){
			var ctx=This.ogg_start(set);
			if(ctx){
				if(ctx.isW){
					This.ogg_encode(ctx,res);
					This.ogg_complete(ctx,True,False,1);
					return;
				}
				This.ogg_stop(ctx);
			};
		};
		
		
		var bitV=GetBitRate(bitRate);
		set.bitRate=bitV.bitRate;
		
		var ogg = new Recorder.OggVorbisEncoder(set.sampleRate, 1, bitV.val);
		
		var blockSize=set.sampleRate;
		var memory=new Uint8Array(500000), mOffset=0;
		
		var idx=0,isFlush=0;
		var run=function(){
			try{
				if(idx<size){
					var buf=ogg.encode([res.subarray(idx,idx+blockSize)]);
				}else{
					isFlush=1;
					var buf=ogg.flush();
				};
			}catch(e){ //精简代码调用了abort
				console.error(e);
				if(!isFlush) try{ ogg.flush() }catch(r){ console.error(r) }
				False("Ogg Encoder: "+e.message);
				return;
			};
			if(buf.length>0){
				var bufLen=buf.length;
				if(mOffset+bufLen>memory.length){
					var tmp=new Uint8Array(memory.length+Math.max(500000,bufLen));
					tmp.set(memory.subarray(0, mOffset));
					memory=tmp;
				}
				memory.set(buf,mOffset);
				mOffset+=bufLen;
			};
			
			if(idx<size){
				idx+=blockSize;
				setTimeout(run);//尽量避免卡ui
			}else{
				True(memory.buffer.slice(0,mOffset),"audio/ogg");
			};
		};
		run();
	}


//********边录边转码(Worker)支持函数，如果提供就代表可能支持，否则只支持标准转码*********

//全局共享一个Worker，后台串行执行。如果每次都开一个新的，编码速度可能会慢很多，可能是浏览器运行缓存的因素，并且可能瞬间产生多个并行操作占用大量cpu
var oggWorker;
Recorder.BindDestroy("oggWorker",function(){
	if(oggWorker){
		Recorder.CLog("oggWorker Destroy");
		oggWorker.terminate();
		oggWorker=null;
	};
});


Recorder.prototype.ogg_envCheck=function(envInfo,set){//检查环境下配置是否可用
	var errMsg="";
	//需要实时编码返回数据，此时需要检查是否可实时编码
	if(set.takeoffEncodeChunk){
		if(!newContext()){//浏览器不能创建实时编码环境
			errMsg=$T("5si6::当前浏览器版本太低，无法实时处理");
		};
	};
	if(!errMsg && !Recorder.OggVorbisEncoder){
		errMsg=ImportEngineErr();
	};
	return errMsg;
};
Recorder.prototype.ogg_start=function(set){//如果返回null代表不支持
	return newContext(set);
};
var openList={id:0};
var newContext=function(setOrNull,_badW){
	//独立运行的函数，scope.wkScope worker.onmessage 字符串会被替换
	var run=function(e){
		var ed=e.data;
		var wk_ctxs=scope.wkScope.wk_ctxs;
		var wk_OggEnc=scope.wkScope.wk_OggEnc;
		
		var cur=wk_ctxs[ed.id];
		if(ed.action=="init"){
			wk_ctxs[ed.id]={
				takeoff:ed.takeoff
				
				,memory:new Uint8Array(500000), mOffset:0
				,encObj:new wk_OggEnc(ed.sampleRate, 1, ed.bitVv)
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
				var buf=cur.encObj.encode([ed.pcm]);
			}catch(e){ //精简代码调用了abort
				cur.err=e;
				console.error(e);
			};
			if(buf && buf.length>0){
				if(cur.takeoff){
					worker.onmessage({action:"takeoff",id:ed.id,chunk:buf});
				}else{
					addBytes(buf);
				};
			};
			break;
		case "complete":
			cur.isCp=1;
			try{
				var buf=cur.encObj.flush();
			}catch(e){ //精简代码调用了abort
				cur.err=e;
				console.error(e);
			};
			if(buf && buf.length>0){
				if(cur.takeoff){
					worker.onmessage({action:"takeoff",id:ed.id,chunk:buf});
				}else{
					addBytes(buf);
				};
			};
			if(cur.err){
				worker.onmessage({action:ed.action,id:ed.id
					,err:"Ogg Encoder: "+cur.err.message});
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
					//取走实时生成的ogg数据
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
			
			var bitV=GetBitRate(setOrNull.bitRate);
			setOrNull.bitRate=bitV.bitRate;
			
			var takeoff=!!setOrNull.takeoffEncodeChunk;
			if(takeoff){
				Recorder.CLog($T("R8yz::takeoffEncodeChunk接管OggVorbis编码器输出的二进制数据，Ogg由数据页组成，一页包含多帧音频数据（含几秒的音频，一页数据无法单独解码和播放），此编码器每次输出都是完整的一页数据，因此实时性会比较低；在合并成完整ogg文件时，必须将输出的所有数据合并到一起，否则可能无法播放，不支持截取中间一部分单独解码和播放"),3);
			};
			
			worker.postMessage({
				action:"init"
				,id:ctx.id
				,sampleRate:setOrNull.sampleRate
				,bitRate:setOrNull.bitRate, bitVv:bitV.val
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
	var scope,worker=oggWorker;
	
	//非浏览器，不支持worker，或者开启失败，使用UI线程处理
	if(_badW || !HasWebWorker){
		Recorder.CLog($T("hB9D::当前环境不支持Web Worker，OggVorbis实时编码器运行在主线程中"),3);
		worker={ postMessage:function(ed){ run({data:ed}); } };
		scope={wkScope:{
			wk_ctxs:{}, wk_OggEnc:Recorder.OggVorbisEncoder
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
			jsCode+=";var wkScope={ wk_ctxs:{},wk_OggEnc:Create() };";
			if(Recorder.OggVorbisEncoder.Module.StaticSeed){
				jsCode+="wkScope.wk_OggEnc.Module.StaticSeed=true;";
			};
			
			var engineCode=Recorder.OggVorbisEncoder.Create.toString();
			var url=(window.URL||webkitURL).createObjectURL(new Blob(["var Create=(",engineCode,jsCode], {type:"text/javascript"}));
			
			worker=new Worker(url);
			setTimeout(function(){
				(window.URL||webkitURL).revokeObjectURL(url);//必须要释放，不然每次调用内存都明显泄露内存
			},10000);//chrome 83 file协议下如果直接释放，将会使WebWorker无法启动
			initOnMsg(1);
		};
		
		var ctx=initCtx(); ctx.isW=1;
		oggWorker=worker;
		return ctx;
	}catch(e){//出错了就不要提供了
		worker&&worker.terminate();
		console.error(e);
		return newContext(setOrNull, 1);//切换到UI线程处理
	};
};
Recorder.prototype.ogg_stop=function(startCtx){
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
			Recorder.CLog($T("oTiy::ogg worker剩{1}个未stop",0,opens),3);
		};
	};
};
Recorder.prototype.ogg_encode=function(startCtx,pcm){
	if(startCtx&&startCtx.worker){
		startCtx.worker.postMessage({
			action:"encode"
			,id:startCtx.id
			,pcm:pcm
		});
	};
};
Recorder.prototype.ogg_complete=function(startCtx,True,False,autoStop){
	var This=this;
	if(startCtx&&startCtx.worker){
		startCtx.call=function(data){
			if(autoStop){
				This.ogg_stop(startCtx);
			};
			if(data.err){
				False(data.err);
			}else{
				True(data.blob,"audio/ogg");
			};
		};
		startCtx.worker.postMessage({
			action:"complete"
			,id:startCtx.id
		});
	}else{
		False($T("dIpw::ogg编码器未start"));
	};
};






/* 编码输出测试，半天才输出一段数据
var ogg = new Recorder.OggVorbisEncoder(16000, 1, -0.1);
for(var i=0;i<10*10;i++){v=ogg.encode([new Array(1600).fill().map(a=>~~(Math.random()*0x7fff))]).length; if(v)console.log(i,v)}
console.log("flush");ogg.flush().length;
*/

//转换比特率成质量数值
var GetBitRate=function(bitRate){
	bitRate=Math.min(Math.max(bitRate,16),100);
	//取值-0.1-1，实际输出16-100kbps
	var val=Math.max(1.1*(bitRate-16)/(100-16)-0.1, -0.1);
	return {bitRate:bitRate,val:val};
};

}));