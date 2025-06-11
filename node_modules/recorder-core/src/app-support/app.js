/*
RecordApp：基于Recorder的跨平台录音，支持在浏览器环境中使用（H5）、各种使用js来构建的程序中使用（App、小程序、UniApp、Electron、NodeJs）
https://github.com/xiangyuecn/Recorder

示例demo请参考根目录内的app-support-sample目录

使用时需先引入recorder-core和需要的编码器，再引入本js，再根据不同平台引入相应的app-xxx-support.js支持文件；如果引入的支持文件需要进行额外的配置，可参考app-support-sample目录内对应的配置文件。

可以仅使用RecordApp作为入口，可以不关心recorder-core中的方法，因为RecordApp已经对他进行了一次封装，并且屏蔽了非通用的功能。
*/
(function(factory){
	var browser=typeof window=="object" && !!window.document;
	var win=browser?window:Object; //非浏览器环境，Recorder挂载在Object下面
	var rec=win.Recorder,ni=rec.i18n;
	factory(win,rec,ni,ni.$T,browser);
	//umd returnExports.js
	if(typeof(define)=='function' && define.amd){
		define(function(){
			return win.RecordApp;
		});
	};
	if(typeof(module)=='object' && module.exports){
		module.exports=win.RecordApp;
	};
}(function(Export,Recorder,i18n,$T,isBrowser){
"use strict";

var App={
LM:"2024-04-09 19:22"

//当前使用的平台实现
,Current:0
//已注册的平台实现
,Platforms:{} 
};
var Platforms=App.Platforms;
var AppTxt="RecordApp";
var ReqTxt="RequestPermission";
var RegTxt="RegisterPlatform";

var WApp2=Export[AppTxt];//重复加载js
if(WApp2&&WApp2.LM==App.LM){
	WApp2.CLog($T("uXtA::重复导入{1}",0,AppTxt),3);
	return;
};
Export[AppTxt]=App;
Recorder[AppTxt]=App;


App.__SID_=0;//同步操作，防止同时多次调用
var SID=App.__SID=function(){ return ++App.__SID_; };
var Sync=App.__Sync=function(sid,tag,err){
	if(App.__SID_!=sid){
		if(tag){
			CLog($T("kIBu::注意：因为并发调用了其他录音相关方法，当前 {1} 的调用结果已被丢弃且不会有回调",0,tag)+(err?", error: "+err:""),3);
		}
		return false;
	}
	return true;
};

var CLog=function(){
	var v=arguments; v[0]="["+(CLog.Tag||AppTxt)+"]["+(App.Current&&App.Current.Key||"?")+"]"+v[0];
	Recorder.CLog.apply(null,v);
};
App.CLog=CLog;


/**
注册一个平台的实现，对应的都会有一个app-xxx-support.js支持文件(Default-H5除外)，config中提供统一的实现接口：
{
	Support: fn( call(canUse) ) 判断此平台是否支持或开启，如果平台可用需回调call(true)选择使用这个平台，并忽略其他平台
	CanProcess: fn() 此平台是否支持实时回调，返回true代表支持
	
	Install: fn( success(),fail(errMsg) ) 可选，平台初始化安装，当使用此平台时会执行一次本方法（同一时间只会有一次调用，没有并发调用问题）
	Pause: fn() 可选，暂停录音实现，如果返回false将执行默认暂停操作
	Resume: fn() 可选，继续录音实现，如果返回false将执行默认继续操作
	
下面的方法中sid用于同步操作，在异步回调中用App.__Sync判断此sid是否处于同步状态
实现中使用到的Recorder实例需赋值给App.__Rec（Stop结束后会自动清理并赋值为null）
	
	RequestPermission:fn(sid,success,fail) 实现录音权限请求，通过回调函数返回结果
		success:fn() 有权限时回调
		fail:fn(errMsg,isUserNotAllow) 没有权限或者不能录音时回调，如果是用户主动拒绝的录音权限，除了有错误消息外，isUserNotAllow=true，方便程序中做不同的提示，提升用户主动授权概率
	
	Start:fn(sid,set,success,fail) 实现开始录音
		set:{} 和Recorder的set大部分参数相同
		success:fn() 打开录音时回调
		fail:fn(errMsg) 开启录音出错时回调
	Start_Check:fn(set) 可选，调用本实现的Start前执行环境检查，返回检查错误文本，如果返回false将执行默认检查操作
	AllStart_Clean:fn(set) 可选，任何实现的Start前执行本配置清理，set里面可能为了兼容不同平台环境会传入额外的参数，可以进行清理，无返回值
	
	Stop:fn(sid,success,fail) 实现结束录音，返回结果，success参数=null时仅清理资源
		success:fn(arrayBuffer,duration,mime)	成功完成录音回调，参数可能为null
			arrayBuffer:ArrayBuffer 录音数据
			duration:123 //录音数据持续时间
			mime:"audio/mp3" 录音数据格式
		fail:fn(errMsg) 录音出错时回调
}
**/
App[RegTxt]=function(key,config){ //App.RegisterPlatform=function()
	config.Key=key;
	if(Platforms[key]){
		CLog($T("ha2K::重复注册{1}",0,key),3);
	}
	Platforms[key]=config;
};
App.__StopOnlyClearMsg=function(){
	return $T("wpTL::仅清理资源");
};

/****实现默认的H5统一接口*****/
var KeyH5="Default-H5",H5OpenSet=ReqTxt+"_H5OpenSet";
(function(){
var impl={
	Support:function(call){
		//默认的始终要支持
		call(true);
	}
	,CanProcess:function(){
		return true;//支持实时回调
	}
};
App[RegTxt](KeyH5,impl);

impl[ReqTxt]=function(sid,success,fail){ //impl.RequestPermission=function()
	var old=App.__Rec;
	if(old){
		old.close();
		App.__Rec=null;
	};
	h5Kill();
	
	//h5会提前打开录音，open时需要的配置只能单独配置
	var h5Set=App[H5OpenSet]; App[H5OpenSet]=null;
	
	var rec=Recorder(h5Set||{});
	rec.open(function(){
		//rec.close(); keep stream Stop时再关，免得Start再次请求权限
		success();
	},fail);
};
var h5Kill=function(){ //释放检测权限时已打开的录音
	if(Recorder.IsOpen()){
		CLog("kill open...");
		var rec=Recorder();
		rec.open();
		rec.close();
	};
};
impl.Start=function(sid,set,success,fail){
	var appRec=App.__Rec;
	if(appRec!=null){
		appRec.stop();//未stop的stop掉
	};
	App.__Rec=appRec=Recorder(set);
	appRec.appSet=set;
	appRec.dataType="arraybuffer";
	appRec.open(function(){
		if(Sync(sid)){
			appRec.start();
		};
		success();
	},fail);
};
impl.Stop=function(sid,success,fail){
	var appRec=App.__Rec;
	var clearMsg=success?"":App.__StopOnlyClearMsg();
	if(!appRec){
		h5Kill(); //释放检测权限时已打开的录音
		fail($T("bpvP::未开始录音")
			+(clearMsg?" ("+clearMsg+")":""));
		return;
	};
	var end=function(){
		if(Sync(sid)){
			appRec.close();
			//把可能变更的配置写回去
			for(var k in appRec.set){
				appRec.appSet[k]=appRec.set[k];
			};
		};
	};
	
	var stopFail=function(msg){
		end();
		fail(msg);
	};
	if(!success){
		stopFail(clearMsg);
		return;
	};
	appRec.stop(function(arrBuf,duration,mime){
		end();
		success(arrBuf,duration,mime);
	},stopFail);
};

})();





/***
获取底层平台录音过程中会使用用来处理实时数据的Recorder对象实例rec，如果底层录音过程中不使用Recorder进行数据的实时处理（目前没有），将返回null。Start调用前和Stop调用后均会返回null。

rec中的方法不一定都能使用，主要用来获取内部缓冲用的，比如实时清理缓冲。
***/
App.GetCurrentRecOrNull=function(){
	return App.__Rec||null;
};

/**暂停录音**/
App.Pause=function(){
	var cur=App.Current,key="Pause";
	if(cur&&cur[key]){
		if(cur[key]()!==false)return;
	}
	var rec=App.__Rec;
	if(rec && canProc(key)){
		rec.pause();
	}
};
/**恢复录音**/
App.Resume=function(){
	var cur=App.Current,key="Resume";
	if(cur&&cur[key]){
		if(cur[key]()!==false)return;
	}
	var rec=App.__Rec;
	if(rec && canProc(key)){
		rec.resume();
	}
};
var canProc=function(tag){
	var cur=App.Current;
	if(cur&&cur.CanProcess()) return 1;
	CLog($T("fLJD::当前环境不支持实时回调，无法进行{1}",0,tag),3);
};


/***
初始化安装，可反复调用
success: fn() 初始化成功
fail: fn(msg) 初始化失败
***/
App.Install=function(success,fail){
	var cur=App.Current;
	if(cur){ success&&success(); return; }
	//因为此操作是异步的，为了避免竞争Current资源，此代码保证得到结果前只会发起一次调用
	var reqs=App.__reqs||(App.__reqs=[]);
	reqs.push({s:success,f:fail});
	success=function(){ call("s",arguments) };
	fail=function(){ call("f",arguments) };
	var call=function(fn,args){
		var arr=[].concat(reqs); reqs.length=0;
		for(var i=0;i<arr.length;i++){
			var f=arr[i][fn];
			f&&f.apply(null,args);
		};
	};
	if(reqs.length>1) return;
	
	var keys=[KeyH5],key;
	for(var k in Platforms){
		if(k!=KeyH5)keys.push(k);
	}
	keys.reverse();
	var initCur=function(idx){
		key=keys[idx];
		cur=Platforms[key];
		cur.Support(function(canUse){
			if(!canUse){
				return initCur(idx+1);
			};
			if(cur.Install){
				cur.Install(initOk,fail);
			}else{
				initOk();
			};
		});
	};
	var initOk=function(){
		App.Current=cur;
		CLog("Install platform: "+key);
		success();
	};
	initCur(0);
};


/***
请求录音权限，如果当前环境不支持录音或用户拒绝将调用错误回调，调用start前需先至少调用一次此方法；请求权限后如果不使用了，不管有没有调用Start，至少要调用一次Stop来清理可能持有的资源。
success:fn() 有权限时回调
fail:fn(errMsg,isUserNotAllow) 没有权限或者不能录音时回调，如果是用户主动拒绝的录音权限，除了有错误消息外，isUserNotAllow=true，方便程序中做不同的提示，提升用户主动授权概率
***/
App[ReqTxt]=function(success,fail){ //App.RequestPermission=function(success,fail){
	var sid=SID(),tag=AppTxt+"."+ReqTxt;
	var failCall=function(errMsg,isUserNotAllow){
		isUserNotAllow=!!isUserNotAllow;
		var msg=errMsg+", isUserNotAllow:"+isUserNotAllow;
		if(!Sync(sid,tag,msg))return;
		CLog($T("YnzX::录音权限请求失败：")+msg,1);
		fail&&fail(errMsg,isUserNotAllow);
	};
	CLog(ReqTxt+"...");
	App.Install(function(){
		if(!Sync(sid,tag))return;
		
		var checkMsg=CheckH5();
		if(checkMsg){ failCall(checkMsg); return; };
		
		App.Current[ReqTxt](sid,function(){ //App.Current.RequestPermission()
			if(!Sync(sid,tag))return;
			CLog(ReqTxt+" Success");
			success&&success();
		},failCall);
	},failCall);
};
var NeedReqMsg=function(){
	return $T("nwKR::需先调用{1}",0,ReqTxt);
};
var CheckH5=function(){
	var msg="";
	if(App.Current.Key==KeyH5 && !isBrowser){
		msg=$T("citA::当前不是浏览器环境，需引入针对此平台的支持文件（{1}），或调用{2}自行实现接入",0,"src/app-support/app-xxx-support.js",AppTxt+"."+RegTxt);
	};
	return msg;
};


/***
开始录音，需先调用RequestPermission获得录音权限

set：设置默认值：{
	type:"mp3"//最佳输出格式，如果底层实现能够支持就应当优先返回此格式
	sampleRate:16000//最佳采样率hz
	bitRate:16//最佳比特率kbps
	onProcess:NOOP //如果当前环境支持实时回调（RecordApp.Current.CanProcess()），接收到录音数据时的回调函数：fn(buffers,powerLevel,bufferDuration,bufferSampleRate)
	takeoffEncodeChunk:NOOP //fn(chunkBytes) 
} 注意：此对象会被修改，因为平台实现时需要把实际使用的值存入此对象
success:fn() 打开录音时回调
fail:fn(errMsg) 开启录音出错时回调
***/
App.Start=function(set,success,fail){
	var sid=SID(),tag=AppTxt+".Start";
	var failCall=function(msg){
		if(!Sync(sid,tag,msg))return;
		CLog($T("ecp9::开始录音失败：")+msg,1);
		fail&&fail(msg);
	};
	CLog("Start...");
	
	var cur=App.Current;
	if(!cur){
		failCall(NeedReqMsg());
		return;
	};
	
	set||(set={});
	var obj={
		type:"mp3"
		,sampleRate:16000
		,bitRate:16
		,onProcess:function(){}
	};
	for(var k in obj){
		set[k]||(set[k]=obj[k]);
	};
	
	//对配置项进行清理，set里面可能为了兼容不同平台环境会传入额外的参数，可以进行清理
	for(var k in Platforms){
		var pf=Platforms[k];
		if(pf.AllStart_Clean){
			pf.AllStart_Clean(set);
		}
	};
	
	//先执行一下环境配置检查
	var checkMsg=false;
	if(cur.Start_Check){
		checkMsg=cur.Start_Check(set);
	};
	if(checkMsg===false){
		var checkRec=Recorder(set);
		checkMsg=checkRec.envCheck({envName:cur.Key,canProcess:cur.CanProcess()});
		if(!checkMsg) checkMsg=CheckH5();
	}
	if(checkMsg){
		failCall($T("EKmS::不能录音：")+checkMsg);
		return;
	};
	//重置Stop时的rec
	App._SRec=0;
	
	cur.Start(sid,set,function(){
		if(!Sync(sid,tag))return;
		CLog($T("k7Qo::已开始录音"),set);
		App._STime=Date.now();
		success&&success();
	},failCall);
};


/***
结束录音

success:fn(arrayBuffer,duration,mime)	结束录音时回调
	arrayBuffer:ArrayBuffer 录音二进制数据
	duration:123 录音时长，单位毫秒
	mime:"auido/mp3" 录音格式类型
	
fail:fn(errMsg) 录音出错时回调

本方法可以用来清理持有的资源，如果不提供success参数=null时，将不会进行音频编码操作，只进行清理完可能持有的资源后走fail回调
***/
App.Stop=function(success,fail){
	var sid=SID(),tag=AppTxt+".Stop";
	var failCall=function(msg){
		if(!Sync(sid,tag,msg))return;
		CLog($T("Douz::结束录音失败：")+msg,success?1:0);
		try{
			fail&&fail(msg);
		}finally{ clear() }
	};
	var clear=function(){
		App._SRec=App.__Rec;
		App.__Rec=null;
	};
	CLog("Stop... "+$T("wqSH::和Start时差：{1}ms",0,App._STime?Date.now()-App._STime:-1)+" Recorder.LM:"+Recorder.LM+" "+AppTxt+".LM:"+App.LM);
	var t1=Date.now();

	var cur=App.Current;
	if(!cur){
		failCall(NeedReqMsg());
		return;
	};
	
	cur.Stop(sid, !success?null:function(arrayBuffer,duration,mime){
		if(!Sync(sid,tag))return;
		CLog($T("g3VX::结束录音 耗时{1}ms 音频时长{2}ms 文件大小{3}b {4}",0,Date.now()-t1,duration,arrayBuffer.byteLength,mime));
		try{
			success(arrayBuffer,duration,mime);
		}finally{ clear() }
	},failCall);
};


}));