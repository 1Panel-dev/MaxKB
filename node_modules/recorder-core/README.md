# Recorder：recorder-core 用于html5录音

GitHub: [https://github.com/xiangyuecn/Recorder](https://github.com/xiangyuecn/Recorder)

Gitee: [https://gitee.com/xiangyuecn/Recorder](https://gitee.com/xiangyuecn/Recorder)

文档和详细使用方法请参考上面两个Recorder仓库。npm recorder这个名字已被使用，因此在Recorder基础上增加后缀-core，就命名为recorder-core，和Recorder核心文件同名。


# 如何使用

## 使用npm安装
```
npm install recorder-core
```

## 引入Recorder库
可以使用`import`、`require`、`html script`等你适合的方式来引入js文件，下面的以import为主要参考，其他引入方式根据文件路径自行调整一下就可以了。
``` javascript
//必须引入的Recorder核心（文件路径是 /src/recorder-core.js 下同），使用import、require都行；recorder-core会自动往window（浏览器环境）或Object（非浏览器环境）下挂载名称为Recorder对象，全局可调用Recorder
import Recorder from 'recorder-core' //注意如果未引用Recorder变量，可能编译时会被优化删除（如vue3 tree-shaking），请改成 import 'recorder-core'，或随便调用一下 Recorder.a=1 保证强引用
//import './你clone的目录/src/recorder-core.js' //clone源码可以按这个方式引入，下同
//require('./你clone的目录/src/recorder-core.js') //clone源码可以按这个方式引入，下同
//<script src="你clone的目录/src/recorder-core.js"> //这是html中script方式引入，下同

//按需引入你需要的录音格式支持文件，如果需要多个格式支持，把这些格式的编码引擎js文件统统引入进来即可
import 'recorder-core/src/engine/mp3'
import 'recorder-core/src/engine/mp3-engine' //如果此格式有额外的编码引擎（*-engine.js）的话，必须要加上

//以上三个也可以合并使用压缩好的recorder.xxx.min.js
//比如 import 'recorder-core/recorder.mp3.min' //已包含recorder-core和mp3格式支持
//比如 <script src="你clone的目录/recorder.mp3.min.js">

//可选的插件支持项，把需要的插件按需引入进来即可
import 'recorder-core/src/extensions/waveview'

/****以上均为Recorder的相关文件，下面是RecordApp需要的支持文件****/

//必须引入的RecordApp核心文件（文件路径是 /src/app-support/app.js）。注意：app.js会自动往window（浏览器环境）或Object（非浏览器环境）下挂载名称为RecordApp对象，全局可调用RecordApp
import RecordApp from 'recorder-core/src/app-support/app'

//引入特定平台环境下的支持文件（也可以统统引入进来，非对应的环境下运行时会忽略掉）
//import 'recorder-core/src/app-support/app-native-support.js' //App下的原生录音支持文件（App中未提供原生支持时可以不提供，统统走H5录音）
//import 'recorder-core/src/app-support/app-miniProgram-wx-support.js' //微信小程序下的录音支持文件
//import '@/uni_modules/Recorder-UniCore/app-uni-support.js' //uni-app下的支持文件，请参考本文档目录下的demo_UniApp测试项目

//ts import 提示：npm包内已自带了.d.ts声明文件（不过是any类型）
```

## Recorder调用录音
这里假设只录3秒，录完后立即播放，[在线编辑运行此代码>>](https://xiangyuecn.github.io/Recorder/assets/工具-代码运行和静态分发Runtime.html?idf=self_base_demo)。录音结束后得到的是Blob二进制文件对象，可以下载保存成文件、用`FileReader`读取成`ArrayBuffer`或者`Base64`给js处理，或者参考下一节上传示例直接上传。
``` javascript
//简单控制台直接测试方法：在任意(无CSP限制)页面内加载需要的js，加载成功后再执行一次本代码立即会有效果
//①加载Recorder+mp3：await import("https://unpkg.com/recorder-core/recorder.mp3.min.js"); console.log("import ok")
//②可视化插件和显示：await import("https://unpkg.com/recorder-core/src/extensions/waveview.js"); console.log("import ok"); div=document.createElement("div");div.innerHTML='<div style="height:100px;width:300px;" class="recwave"></div>';document.body.prepend(div);

var rec,processTime,wave;
/**调用open打开录音请求好录音权限**/
var recOpen=function(success){//一般在显示出录音按钮或相关的录音界面时进行此方法调用，后面用户点击开始录音时就能畅通无阻了
    rec=Recorder({ //本配置参数请参考下面的文档，有详细介绍
        type:"mp3",sampleRate:16000,bitRate:16 //mp3格式，指定采样率hz、比特率kbps，其他参数使用默认配置；注意：是数字的参数必须提供数字，不要用字符串；需要使用的type类型，需提前把格式支持文件加载进来，比如使用wav格式需要提前加载wav.js编码引擎
        ,onProcess:function(buffers,powerLevel,bufferDuration,bufferSampleRate,newBufferIdx,asyncEnd){
            //录音实时回调，大约1秒调用12次本回调，buffers为开始到现在的所有录音pcm数据块(16位小端LE)
            //可利用extensions/sonic.js插件实时变速变调，此插件计算量巨大，onProcess需要返回true开启异步模式
            //可实时上传（发送）数据，配合Recorder.SampleData方法，将buffers中的新数据连续的转换成pcm上传，或使用mock方法将新数据连续的转码成其他格式上传，可以参考文档里面的：Demo片段列表 -> 实时转码并上传-通用版；基于本功能可以做到：实时转发数据、实时保存数据、实时语音识别（ASR）等
            processTime=Date.now();

            //可实时绘制波形（extensions目录内的waveview.js、wavesurfer.view.js、frequency.histogram.view.js插件功能）
            wave&&wave.input(buffers[buffers.length-1],powerLevel,bufferSampleRate);
        }
    });

    rec.open(function(){//打开麦克风授权获得相关资源
        //rec.start() 此处可以立即开始录音，但不建议这样编写，因为open是一个延迟漫长的操作，通过两次用户操作来分别调用open和start是推荐的最佳流程

        //创建可视化，指定一个要显示的div
        if(Recorder.WaveView)wave=Recorder.WaveView({elem:".recwave"});
        success&&success();
    },function(msg,isUserNotAllow){//用户拒绝未授权或不支持
        console.log((isUserNotAllow?"UserNotAllow，":"")+"无法录音:"+msg);
    });
};

/**开始录音**/
function recStart(){//打开了录音后才能进行start、stop调用
    rec.start();
    
    //【稳如老狗WDT】可选的，监控是否在正常录音有onProcess回调，如果长时间没有回调就代表录音不正常
    var wdt=rec.watchDogTimer=setInterval(function(){
        if(!rec || wdt!=rec.watchDogTimer){ clearInterval(wdt); return } //sync
        if(Date.now()<rec.wdtPauseT) return; //如果暂停录音了就不检测：puase时赋值rec.wdtPauseT=Date.now()*2（永不监控），resume时赋值rec.wdtPauseT=Date.now()+1000（1秒后再监控）
        if(Date.now()-(processTime||startTime)>1500){ clearInterval(wdt);
            console.error(processTime?"录音被中断":"录音未能正常开始");
            // ... 错误处理，关闭录音，提醒用户
        }
    },1000);
    var startTime=Date.now(); rec.wdtPauseT=0; processTime=0;
};

/**结束录音**/
function recStop(){
    rec.watchDogTimer=0; //停止监控onProcess超时
    rec.stop(function(blob,duration){
        
        //简单利用URL生成本地文件地址，注意不用了时需要revokeObjectURL，否则霸占内存
        //此地址只能本地使用，比如赋值给audio.src进行播放，赋值给a.href然后a.click()进行下载（a需提供download="xxx.mp3"属性）
        var localUrl=(window.URL||webkitURL).createObjectURL(blob);
        console.log(blob,localUrl,"时长:"+duration+"ms");
        rec.close();//释放录音资源，当然可以不释放，后面可以连续调用start；但不释放时系统或浏览器会一直提示在录音，最佳操作是录完就close掉
        rec=null;
        
        //已经拿到blob文件对象想干嘛就干嘛：立即播放、上传、下载保存
        
        /*** 【立即播放例子】 ***/
        var audio=document.createElement("audio");
        document.body.prepend(audio);
        audio.controls=true;
        audio.src=localUrl;
        audio.play();
    },function(msg){
        console.log("录音失败:"+msg);
        rec.close();//可以通过stop方法的第3个参数来自动调用close
        rec=null;
    });
};


//这里假设立即运行，只录3秒，录完后立即播放，本段代码copy到控制台内可直接运行
recOpen(function(){
    recStart();
    setTimeout(recStop,3000);
});
```

## RecordApp调用录音
RecordApp的基础调用方式在所有平台环境下是通用的；但不同环境下可能会提供更多的方法、或配置参数以供使用，多出来的请参考对应的平台环境支持说明。

``` javascript
/**请求录音权限，Start调用前至少要调用一次RequestPermission**/
var recReq=function(success){
    //RecordApp.RequestPermission_H5OpenSet={ audioTrackSet:{ noiseSuppression:true,echoCancellation:true,autoGainControl:true } }; //这个是Start中的audioTrackSet配置，在h5中必须提前配置，因为h5中RequestPermission会直接打开录音
    
    RecordApp.RequestPermission(function(){
        //注意：有使用到H5录音时，为了获得最佳兼容性，建议RequestPermission、Start至少有一个应当在用户操作（触摸、点击等）下进行调用
        success&&success();
    },function(msg,isUserNotAllow){//用户拒绝未授权或不支持
        console.log((isUserNotAllow?"UserNotAllow，":"")+"无法录音:"+msg);
    });
};

/**开始录音**/
var recStart=function(success){
    var processTime=0;
    
    //开始录音的参数和Recorder的初始化参数大部分相同
    RecordApp.Start({
        type:"mp3",sampleRate:16000,bitRate:16 //mp3格式，指定采样率hz、比特率kbps，其他参数使用默认配置；注意：是数字的参数必须提供数字，不要用字符串；需要使用的type类型，需提前把格式支持文件加载进来，比如使用wav格式需要提前加载wav.js编码引擎
        /*,audioTrackSet:{ //可选，如果需要同时播放声音（比如语音通话），需要打开回声消除（打开后声音可能会从听筒播放，部分环境下（如小程序、uni-app原生接口）可调用接口切换成扬声器外放）
            //注意：H5中需要在请求录音权限前进行相同配置RecordApp.RequestPermission_H5OpenSet后此配置才会生效
            echoCancellation:true,noiseSuppression:true,autoGainControl:true} */
        ,onProcess:function(buffers,powerLevel,bufferDuration,bufferSampleRate,newBufferIdx,asyncEnd){
            //录音实时回调，大约1秒调用12次本回调，buffers为开始到现在的所有录音pcm数据块(16位小端LE)
            //可实时上传（发送）数据，可实时绘制波形，ASR语音识别，使用可参考Recorder
            processTime=Date.now();
        }
        
        //...  不同环境的专有配置，根据文档按需配置
    },function(){
        //开始录音成功
        success&&success();
        
        //【稳如老狗WDT】可选的，监控是否在正常录音有onProcess回调，如果长时间没有回调就代表录音不正常
        var this_=   RecordApp; //有this就用this，没有就用一个全局对象
        if(RecordApp.Current.CanProcess()){
            var wdt=this_.watchDogTimer=setInterval(function(){
                if(wdt!=this_.watchDogTimer){ clearInterval(wdt); return } //sync
                if(Date.now()<this_.wdtPauseT) return; //如果暂停录音了就不检测：puase时赋值this_.wdtPauseT=Date.now()*2（永不监控），resume时赋值this_.wdtPauseT=Date.now()+1000（1秒后再监控）
                if(Date.now()-(processTime||startTime)>1500){ clearInterval(wdt);
                    console.error(processTime?"录音被中断":"录音未能正常开始");
                    // ... 错误处理，关闭录音，提醒用户
                }
            },1000);
        }else{
            console.warn("当前环境不支持onProcess回调，不启用watchDogTimer"); //目前都支持回调
        }
        var startTime=Date.now(); this_.wdtPauseT=0;
    },function(msg){
        console.log("开始录音失败："+msg);
    });
};


//暂停录音
var recPause=function(){
    if(RecordApp.GetCurrentRecOrNull()){
        RecordApp.Pause();
        var this_=RecordApp;this_.wdtPauseT=Date.now()*2; //永不监控onProcess超时
        console.log("已暂停");
    }
};
//继续录音
var recResume=function(){
    if(RecordApp.GetCurrentRecOrNull()){
        RecordApp.Resume();
        var this_=RecordApp;this_.wdtPauseT=Date.now()+1000; //1秒后再监控onProcess超时
        console.log("继续录音中...");
    }
};


/**停止录音，清理资源**/
var recStop=function(){
    var this_=RecordApp;this_.watchDogTimer=0; //停止监控onProcess超时
    
    RecordApp.Stop(function(arrayBuffer,duration,mime){
        //arrayBuffer就是录音文件的二进制数据，不同平台环境下均可进行播放、上传
        console.log(arrayBuffer,mime,"时长:"+duration+"ms");
        
        //如果当前环境支持Blob，也可以直接构造成Blob文件对象，和Recorder使用一致
        if(typeof(Blob)!="undefined" && typeof(window)=="object"){
            var blob=new Blob([arrayBuffer],{type:mime});
            console.log(blob, (window.URL||webkitURL).createObjectURL(blob));
        }
    },function(msg){
        console.log("录音失败:"+msg);
    });
};


//这里假设立即运行，只录3秒
recReq(function(){
    recStart(function(){
        setTimeout(recStop,3000);
    });
});
```




