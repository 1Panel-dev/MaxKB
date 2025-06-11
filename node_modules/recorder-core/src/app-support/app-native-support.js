/*
录音 RecordApp: App Native支持文件，支持在浏览器环境中使用（Hybrid App）、各种适配后的js运行环境中使用（非浏览器环境）
https://github.com/xiangyuecn/Recorder

特别注明：本文件涉及的功能需要iOS、Android等App端提供的原生支持，如果你不能修改App的源码，并且坚决要使用本文件，那将会很困难。

如果是在App内置的浏览器中进行录音（Hybrid App），应当首选使用Recorder H5进行录音；RecordApp+Native也可以在非浏览器环境中使用，比如：只有js运行时的app环境、nodejs环境。

录音功能由原生App(Native)代码实现，通过JsBridge和js进行交互。Native层需要提供：请求权限、开始录音、结束录音、定时回调PCM[Int16]片段 等功能和接口。因为js层已加载Recorder和相应的js编码引擎，所以，Native层无需进行编码，可大大简化App的逻辑。

录音必须是单声道的，因为这个库从头到尾就没有打算支持双声道。

JsBridge可以是自己实现的交互方式 或 别人提供的框架。因为不知道具体使用的桥接方式，对应的请求已抽象成了4个方法在Native.Config中，需自行实现。

注意：此文件并非拿来就能用的，需要改动【需实现】标注的地方；也可以不改动此文件，使用另外的初始化配置文件来进行配置，可参考app-support-sample目录内的配置文件，另外这个目录内还有Android和iOS的demo项目，copy源码改改就能用。

如果是App内置的浏览器中使用时（H5），支持在iframe中使用，但如果是跨域要特殊处理。
*/
(function(factory){
	var browser=typeof window=="object" && !!window.document;
	var win=browser?window:Object; //非浏览器环境，Recorder挂载在Object下面
	var rec=win.Recorder,ni=rec.i18n;
	factory(rec,ni,ni.$T,browser);
}(function(Recorder,i18n,$T,isBrowser){
"use strict";

var App=Recorder.RecordApp;
var CLog=App.CLog;

var platform={
	Support:function(call){
		if(!App.AlwaysAppUseH5){
			config.IsApp(call);
			return;
		};
		//不支持app原生录音
		call(false);
	}
	,CanProcess:function(){
		return true;//支持实时回调
	}
	,Config:{
		IsApp:function(call){
			//如需打开原生App支持，此方法【需实现】，此方法用来判断：1. 判断app是否是在环境中 2. app支持录音
			NeedConfigMsg("IsApp");
			call(false);//默认实现不支持app原生录音，支持就回调call(true)
		}
		,JsBridgeRequestPermission:function(success,fail){
			/*如需打开原生App支持，此方法【需实现】
				success:fn() 有权限时回调
				fail:fn(errMsg,isUserNotAllow) 出错回调
			*/
			fail(NeedConfigMsg("JsBridgeRequestPermission"));
		}
		,JsBridgeStart:function(set,success,fail){
			/*如需打开原生App支持，此方法【需实现】，app打开录音后原生层定时返回PCM数据时JsBridge js层需要回调set.onProcess。建议JsBridge增加一个Alive接口，为录音时定时心跳请求，如果网页超过10秒未调用此接口，app原生层自动停止录音，防止stop不能调用导致的资源泄露。
				set:RecordApp.Start的set参数
				success:fn() 打开录音时回调
				fail:fn(errMsg) 开启录音出错时回调
			*/
			fail(NeedConfigMsg("JsBridgeStart"));
		}
		,JsBridgeStop:function(success,fail){
			/*如需打开原生App支持，此方法【需实现】
				success:fn() 结束录音时回调
				fail:fn(errMsg) 结束录音出错时回调
			*/
			fail(NeedConfigMsg("JsBridgeStop"));
		}
	}
};
App.RegisterPlatform("Native",platform);
var config=platform.Config;

var NeedConfigMsg=function(fn){
	var msg=$T("WWoj::{1}中的{2}方法未实现，请在{3}文件中或配置文件中实现此方法",0,"RecordApp.Platforms.Native.Config",fn,"app-native-support.js");
	CLog(msg,3);
	return msg;
};


/*******App Native层在录音时定时回调本js方法*******/
/*
pcmDataBase64: base64<Int16[]>字符串 当前单声道录音缓冲PCM片段，正常情况下为上次回调本接口开始到现在的录音数据，Int16[]二进制数组需要编码成base64字符串；或者直接传一个Int16Array对象
sampleRate：123456 录制音频实际的采样率
*/
var onRecFn=function(pcmDataBase64,sampleRate){
	var rec=onRecFn.rec;
	if(!rec){
		CLog($T("rCAM::未开始录音，但收到Native PCM数据"),3);
		return;
	};
	if(!rec._appStart){
		rec.envStart({
			envName:platform.Key,canProcess:platform.CanProcess()
		},sampleRate);
	};
	rec._appStart=1;
	
	var sum=0;
	if(pcmDataBase64 instanceof Int16Array){
		var pcm=new Int16Array(pcmDataBase64);
		for(var i=0;i<pcm.length;i++){
			sum+=Math.abs(pcm[i]);
		}
	}else{
		var bstr=atob(pcmDataBase64),n=bstr.length;
		var pcm=new Int16Array(n/2);
		for(var idx=0,s,i=0;i+2<=n;idx++,i+=2){
			s=((bstr.charCodeAt(i)|(bstr.charCodeAt(i+1)<<8))<<16)>>16;
			pcm[idx]=s;
			sum+=Math.abs(s);
		};
	}
	
	rec.envIn(pcm,sum);
};
if(!isBrowser){
	App.NativeRecordReceivePCM=onRecFn;
};
//尝试注入顶层window，用于接收Native回调数据，此处特殊处理一下，省得跨域的iframe无权限
if(isBrowser){
	window.NativeRecordReceivePCM=onRecFn;
	try{
		window.top.NativeRecordReceivePCM=onRecFn;
	}catch(e){
		var tipsFn=function(){
			CLog($T("t2OF::检测到跨域iframe，NativeRecordReceivePCM无法注入到顶层，已监听postMessage转发兼容传输数据，请自行实现将top层接收到数据转发到本iframe（不限层），不然无法接收到录音数据"),3);
		};
		setTimeout(tipsFn,8000);
		tipsFn();
		
		addEventListener("message",function(e){//纯天然，无需考虑origin
			var data=e.data;//{type:"",data:{pcmDataBase64:"",sampleRate:16000}}
			if(data&&data.type=="NativeRecordReceivePCM"){
				data=data.data;
				onRecFn(data.pcmDataBase64, data.sampleRate);
			};
		});
	};
};





/*******实现统一接口*******/
platform.RequestPermission=function(sid,success,fail){
	config.JsBridgeRequestPermission(success,fail);
};
platform.Start=function(sid,set,success,fail){
	onRecFn.param=set;
	var rec=Recorder(set);
	rec.set.disableEnvInFix=true; //不要音频输入丢失补偿
	rec.dataType="arraybuffer";
	
	onRecFn.rec=rec;//等待第一个数据到来再调用rec.start
	App.__Rec=rec;//App需要暴露出使用到的rec实例
	
	config.JsBridgeStart(set,success,fail);
};
platform.Stop=function(sid,success,fail){
	var failCall=function(msg){
		if(App.__Sync(sid)){
			onRecFn.rec=null;
		}
		fail(msg);
	};
	config.JsBridgeStop(function(){
		if(!App.__Sync(sid)){
			failCall("Incorrect sync status");
			return;
		};
		var rec=onRecFn.rec;
		onRecFn.rec=null;
		
		var clearMsg=success?"":App.__StopOnlyClearMsg();
		if(!rec){
			failCall($T("Z2y2::未开始录音")
				+(clearMsg?" ("+clearMsg+")":""));
			return;
		};
		
		CLog("rec encode: pcm:"+rec.recSize+" srcSR:"+rec.srcSampleRate+" set:"+JSON.stringify(onRecFn.param));
		
		var end=function(){
			if(App.__Sync(sid)){
				//把可能变更的配置写回去
				for(var k in rec.set){
					onRecFn.param[k]=rec.set[k];
				};
			};
		};
		if(!success){
			end();
			failCall(clearMsg);
			return;
		};
		rec.stop(function(arrBuf,duration,mime){
			end();
			success(arrBuf,duration,mime);
		},function(msg){
			end();
			failCall(msg);
		});
	},failCall);
};

}));