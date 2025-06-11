/*
Resorder使用的 AMR格式解码编码器
https://github.com/xiangyuecn/Recorder

由此源码改动而来 （2023-09-25 大幅精简代码，移除了大量从未调用的函数、条件分支）
https://raw.githubusercontent.com/BenzLeung/benz-amr-recorder/462c6b91a67f7d9f42d0579fb5906fad9edb2c9d/src/amrnb.js
*/
(function(factory){
	var browser=typeof window=="object" && !!window.document;
	var win=browser?window:Object; //非浏览器环境，Recorder挂载在Object下面
	var rec=win.Recorder;
	factory(rec);
}(function(Recorder){ //需要在Worker中运行，不能使用Recorder里的方法，包括$T
"use strict";

function Create(){
	//实时解码器
	var Decoder=function(){
		var This=this;
		var decoder = AMR.Decoder_Interface_init();
		
		var buf = Module._malloc(AMR.AMR_BUFFER_COUNT);
		var decodeInBuffer = new Uint8Array(Module.HEAPU8.buffer, buf, AMR.AMR_BUFFER_COUNT);
		buf = Module._malloc(AMR.PCM_BUFFER_COUNT * 2);
		var decodeOutBuffer = new Int16Array(Module.HEAPU8.buffer, buf, AMR.PCM_BUFFER_COUNT);
		
		var lastBytes=[];
		
		This.decode=function(bytes){
			if(lastBytes.length){
				var a2=new Uint8Array(lastBytes.length+bytes.length);
				a2.set(lastBytes);
				a2.set(bytes,lastBytes.length);
				bytes=a2;
			}
			
			var out = null;
			var inOffset = 0, outOffset = 0;
			
			while (inOffset + 1 < bytes.length) {
				var size = AMR.SIZES[bytes[inOffset] >> 3 & 15];
				if(size==null) throw new Error("Invalid amr frame type: "+bytes[inOffset]);
				size=size+1;
				if(!out) out=new Int16Array(Math.floor(bytes.length / Math.max(13,size) * AMR.PCM_BUFFER_COUNT));
				if (inOffset + size > bytes.length) {
					break
				}
				decodeInBuffer.set(bytes.subarray(inOffset, inOffset + size));
				AMR.Decoder_Interface_Decode(decoder, decodeInBuffer.byteOffset, decodeOutBuffer.byteOffset, 0);
				if (outOffset + AMR.PCM_BUFFER_COUNT > out.length) {
					var newOut = new Int16Array(out.length * 2);
					newOut.set(out.subarray(0, outOffset));
					out = newOut
				}
				inOffset += size;
				out.set(decodeOutBuffer, outOffset);
				outOffset += AMR.PCM_BUFFER_COUNT;
			}
			lastBytes=bytes.subarray(inOffset);
			return new Int16Array(out==null?0:out.subarray(0, outOffset));
		};
		This.flush=function(){
			Module._free(decodeInBuffer.byteOffset);
			Module._free(decodeOutBuffer.byteOffset);
			AMR.Decoder_Interface_exit(decoder);
			return new Int16Array(0);
		};
	};
	//实时编码器
	var Encoder=function(bitRate){
		var This=this;
		var mode = AMR.Mode[AMR.BitRate(bitRate)];
		var encoder = AMR.Encoder_Interface_init();
		
		var buf = Module._malloc(AMR.PCM_BUFFER_COUNT * 2);
		var encodeInBuffer = new Int16Array(Module.HEAPU8.buffer, buf, AMR.PCM_BUFFER_COUNT);
		buf = Module._malloc(AMR.AMR_BUFFER_COUNT);
		var encodeOutBuffer = new Uint8Array(Module.HEAPU8.buffer, buf, AMR.AMR_BUFFER_COUNT);
		
		var lastPcm=[];
		
		This.encode=function(pcm){//pcm : 8000hz Int16Array
			if(lastPcm.length){
				var pcm2=new Int16Array(lastPcm.length+pcm.length);
				pcm2.set(lastPcm);
				pcm2.set(pcm,lastPcm.length);
				pcm=pcm2;
			}
			
			var blockSize = AMR.SIZES[mode] + 1;
			var out = new Uint8Array(Math.ceil(pcm.length / AMR.PCM_BUFFER_COUNT * blockSize));
			var inOffset = 0, outOffset=0;
			while (inOffset + AMR.PCM_BUFFER_COUNT < pcm.length) {
				encodeInBuffer.set(pcm.subarray(inOffset, inOffset + AMR.PCM_BUFFER_COUNT));
				var n = AMR.Encoder_Interface_Encode(encoder, mode, encodeInBuffer.byteOffset, encodeOutBuffer.byteOffset, 0);
				if (n != blockSize) {
					console.error([n, blockSize]);
					break
				}
				inOffset += AMR.PCM_BUFFER_COUNT;
				out.set(encodeOutBuffer.subarray(0, n), outOffset);
				outOffset += n;
			}
			lastPcm=pcm.subarray(inOffset);
			return new Uint8Array(out.subarray(0, outOffset));
		};
		This.flush=function(){
			Module._free(encodeInBuffer.byteOffset);
			Module._free(encodeOutBuffer.byteOffset);
			AMR.Encoder_Interface_exit(encoder);
			return new Uint8Array(0);
		};
	};
	
	
	var AMR = {
		//获取实时解码器
		GetDecoder:function(){
			return Create().DecG_(); //重新获得一个AMR对象操作，避免出错后内存无法重新分配
		}
		//获取实时编码器
		,GetEncoder:function(bitRate){
			return Create().EncG_(bitRate);
		}
		//解码amr文件得到pcm
		,decode: function (amrBytes,True,False) {
			Create().dec__(amrBytes,True,False);
		}
		//编码pcm成amr文件
		,encode: function (pcm,True,False,bitRate) {//pcm : 8000hz Int16Array
			Create().enc__(pcm,True,False,bitRate);
		}
		
		,DecG_: function(){ return new Decoder() }
		,dec__: function (amrBytes,True,False) {
			var This=this,decode=new Decoder();
			var buffers=[],size=0;
			var endFlush=function(){//flush没有结果，只做释放
				try{ decode.flush() }catch(e){ console.error(e) }
			};
			
			var inOffset=0,hasHead=0;
			if (String.fromCharCode.apply(null, amrBytes.subarray(0, this.AMR_HEADER.length)) == this.AMR_HEADER) {
				inOffset+=this.AMR_HEADER.length; hasHead=1;
			}
			var blockSize=(AMR.SIZES[amrBytes[inOffset] >> 3 & 15]||31)+1;
			blockSize=Math.max(13,blockSize)*1000/20*5; //20ms一帧，一帧13-32字节，5秒数据一次
			var run=function(){
				try{
					var startIdx=inOffset;
					if(startIdx<amrBytes.length){
						inOffset+=blockSize;
						var buf=decode.decode(amrBytes.subarray(startIdx,inOffset));
						buffers.push(buf); size+=buf.length;
					}
					if(inOffset<amrBytes.length){
						setTimeout(run);
						return;
					};
				}catch(e){
					console.error(e);
					endFlush();
					False("AMR Decoder: "+(hasHead?e.message:"Not an amr audio file"));
					return;
				};
				endFlush();
				
				var pcm=new Int16Array(size);
				for(var i=0,j=0;i<buffers.length;i++){
					var buf=buffers[i];
					pcm.set(buf,j); j+=buf.length;
				}
				True(pcm);
			};
			run();
		}
		,EncG_: function(bitRate){ return new Encoder(bitRate) }
		,enc__: function (pcm,True,False,bitRate) {//pcm : 8000hz Int16Array
			var This=this,encode=new Encoder(bitRate);
			var buffers=[This.GetHeader()],size=buffers[0].length;
			var endFlush=function(){//flush没有结果，只做释放
				try{ encode.flush() }catch(e){ console.error(e) }
			};
			
			var blockSize=40000; blockSize-=blockSize%This.PCM_BUFFER_COUNT;//5秒数据一次
			var inOffset=0;
			var run=function(){
				try{
					var startIdx=inOffset;
					if(startIdx<pcm.length){
						inOffset+=blockSize;
						var buf=encode.encode(pcm.subarray(startIdx,inOffset));
						buffers.push(buf); size+=buf.length;
					}
					if(inOffset<pcm.length){
						setTimeout(run);
						return;
					};
				}catch(e){ //精简代码调用了abort
					console.error(e);
					endFlush();
					False("AMR Encoder: "+e.message);
					return;
				};
				endFlush();
				
				var bytes=new Uint8Array(size);
				for(var i=0,j=0;i<buffers.length;i++){
					var buf=buffers[i];
					bytes.set(buf,j); j+=buf.length;
				}
				True(bytes);
			};
			run();
		},
		//获取AMR头二进制数据
		GetHeader:function(){
			var str=this.AMR_HEADER;
			var bytes=new Uint8Array(str.length);
			for(var i=0;i<str.length;i++)bytes[i]=str.charCodeAt(i);
			return bytes;
		},
		//返回一个匹配的比特率
		BitRate:function(bitRate){
			var keys=this.Mode;
			if(bitRate){
				if(keys[bitRate]!=null) return bitRate;
				var s=[];
				for(var k in keys) s.push({v:+k,s:Math.abs((k-bitRate)||(k-12.2))});
				s.sort(function(a,b){return a.s-b.s});
				return s[0].v;
			}
			return 12.2;
		},
		
		//精简
		Mode: {"4.75": 0, "5.15": 1, "5.9": 2, "6.7": 3, "7.4": 4, "7.95": 5, "10.2": 6, "12.2": 7},
		SIZES: [12, 13, 15, 17, 19, 20, 26, 31, 5, 6, 5, 5, 0, 0, 0, 0],
		AMR_BUFFER_COUNT: 32,
		PCM_BUFFER_COUNT: 160,
		AMR_HEADER: "#!AMR\n",
		WAV_HEADER_SIZE: 44
	};
	
	
	
	
    var Module = {
        _main: (function () {
            AMR.Decoder_Interface_init = Module._Decoder_Interface_init;
            AMR.Decoder_Interface_exit = Module._Decoder_Interface_exit;
            AMR.Decoder_Interface_Decode = Module._Decoder_Interface_Decode;
            AMR.Encoder_Interface_init = Module._Encoder_Interface_init;
            AMR.Encoder_Interface_exit = Module._Encoder_Interface_exit;
            AMR.Encoder_Interface_Encode = Module._Encoder_Interface_Encode;
            return 0
        })
    };
    AMR.Module=Module;

    //精简

    var Runtime = {
        //精简
        staticAlloc: (function (size) {
            var ret = STATICTOP;
            STATICTOP = STATICTOP + size | 0;
            STATICTOP = STATICTOP + 15 & -16;
            return ret
        }), dynamicAlloc: (function (size) {
            var ret = DYNAMICTOP;
            DYNAMICTOP = DYNAMICTOP + size | 0;
            DYNAMICTOP = DYNAMICTOP + 15 & -16;
            if (DYNAMICTOP >= TOTAL_MEMORY) {
                var success = enlargeMemory();
                if (!success) {
                    DYNAMICTOP = ret;
                    return 0
                }
            }
            return ret
        }), alignMemory: (function (size, quantum) {
            var ret = size = Math.ceil(size / (quantum ? quantum : 16)) * (quantum ? quantum : 16);
            return ret
        //}), 精简
        }), GLOBAL_BASE: 8
    };
    Module["Runtime"] = Runtime;
    var ABORT = false;
    //精简

    function assert(condition, text) {
        if (!condition) {
            abort("Assertion failed: " + text)
        }
    }

    //精简
    var ALLOC_STATIC = 2;
    var ALLOC_NONE = 4;
    Module["ALLOC_STATIC"] = ALLOC_STATIC;
    Module["ALLOC_NONE"] = ALLOC_NONE;

    function allocate(slab, types, allocator, ptr) {
        var zeroinit, size;
        if (typeof slab === "number") {
            zeroinit = true;
            size = slab
        } else {
            zeroinit = false;
            size = slab.length
        }
        var singleType = typeof types === "string" ? types : null;
        var ret;
        if (allocator == ALLOC_NONE) {
            ret = ptr
        } else {
            if(allocator!=ALLOC_STATIC)abort("fix !ALLOC_STATIC");//精简
            ret = Runtime.staticAlloc(Math.max(size, singleType ? 1 : types.length))
        }
        if (zeroinit) {
            var ptr = ret, stop;
            assert((ret & 3) == 0);
            stop = ret + (size & ~3);
            for (; ptr < stop; ptr += 4) {
                HEAP32[ptr >> 2] = 0
            }
            stop = ret + size;
            while (ptr < stop) {
                HEAP8[ptr++ >> 0] = 0
            }
            return ret
        }
        if (singleType === "i8") {
            if (slab.subarray || slab.slice) {
                HEAPU8.set(slab, ret)
            } else {
                HEAPU8.set(new Uint8Array(slab), ret)
            }
            return ret
        }
        abort("fix allocate")
    }

    Module["allocate"] = allocate;

    //精简

    var PAGE_SIZE = 4096;

    function alignMemoryPage(x) {
        if (x % 4096 > 0) {
            x += 4096 - x % 4096
        }
        return x
    }

    var HEAP;
    var HEAP8, HEAPU8, HEAP16, HEAPU16, HEAP32, HEAPU32, HEAPF32, HEAPF64;
    var STATIC_BASE = 0, STATICTOP = 0, staticSealed = false;
    var STACK_BASE = 0, STACKTOP = 0, STACK_MAX = 0;
    var DYNAMIC_BASE = 0, DYNAMICTOP = 0;

    function enlargeMemory() {
        abort("enlargeMemory")
    }

    var TOTAL_STACK = Module["TOTAL_STACK"] || 65536;
    var TOTAL_MEMORY = Module["TOTAL_MEMORY"] || 524288;
    var totalMemory = 64 * 1024;
    while (totalMemory < TOTAL_MEMORY || totalMemory < 2 * TOTAL_STACK) {
        if (totalMemory < 16 * 1024 * 1024) {
            totalMemory *= 2
        } else {
            totalMemory += 16 * 1024 * 1024
        }
    }
    if (totalMemory !== TOTAL_MEMORY) {
        abort('fix t!==T')
    }
    //精简
    var buffer;
    buffer = new ArrayBuffer(TOTAL_MEMORY);
    HEAP8 = new Int8Array(buffer);
    HEAP16 = new Int16Array(buffer);
    HEAP32 = new Int32Array(buffer);
    HEAPU8 = new Uint8Array(buffer);
    HEAPU16 = new Uint16Array(buffer);
    HEAPU32 = new Uint32Array(buffer);
    HEAPF32 = new Float32Array(buffer);
    HEAPF64 = new Float64Array(buffer);
    HEAP32[0] = 255;
    assert(HEAPU8[0] === 255 && HEAPU8[3] === 0, "fix !LE");
    Module["HEAP"] = HEAP;
    Module["buffer"] = buffer;
    Module["HEAP8"] = HEAP8;
    Module["HEAP16"] = HEAP16;
    Module["HEAP32"] = HEAP32;
    Module["HEAPU8"] = HEAPU8;
    Module["HEAPU16"] = HEAPU16;
    Module["HEAPU32"] = HEAPU32;
    Module["HEAPF32"] = HEAPF32;
    Module["HEAPF64"] = HEAPF64;

    //精简

    if (!Math["imul"] || Math["imul"](4294967295, 5) !== -5) Math["imul"] = function imul(a, b) {
        var ah = a >>> 16;
        var al = a & 65535;
        var bh = b >>> 16;
        var bl = b & 65535;
        return al * bl + (ah * bl + al * bh << 16) | 0
    };
    Math.imul = Math["imul"];
    if (!Math["clz32"]) Math["clz32"] = (function (x) {
        x = x >>> 0;
        for (var i = 0; i < 32; i++) {
            if (x & 1 << 31 - i) return i
        }
        return 32
    });
    Math.clz32 = Math["clz32"];
    var Math_abs = Math.abs;
    var Math_cos = Math.cos;
    var Math_sin = Math.sin;
    var Math_tan = Math.tan;
    var Math_acos = Math.acos;
    var Math_asin = Math.asin;
    var Math_atan = Math.atan;
    var Math_atan2 = Math.atan2;
    var Math_exp = Math.exp;
    var Math_log = Math.log;
    var Math_sqrt = Math.sqrt;
    var Math_ceil = Math.ceil;
    var Math_floor = Math.floor;
    var Math_pow = Math.pow;
    var Math_imul = Math.imul;
    var Math_fround = Math.fround;
    var Math_min = Math.min;
    var Math_clz32 = Math.clz32;
    
    //精简

    STATIC_BASE = 8;
    STATICTOP = STATIC_BASE + 31776;

    //精简 负优化
	Module.b64Atob=function(input) {
		//低版本Worker里面没有atob https://developer.mozilla.org/en-US/docs/Web/API/atob
		//测试： s=new Array(1024*10).fill();s=s.map(v=>String.fromCharCode(~~(Math.random()*256)));t=s.join("");s=btoa(t);b64Atob(s)==atob(s)
		var bc = 0, bs, buffer, idx = 0, output = '';
		while(true){
			buffer = input.charCodeAt(idx++);
			if(!buffer || buffer==61) break //""||"="
			if(buffer>64&&buffer<91) buffer-=65;
			else if(buffer>96&&buffer<123) buffer-=71; //97-26
			else if(buffer>47&&buffer<58) buffer+=4; //48-26-26
			else if(buffer==43) buffer=62;// +
			else if(buffer==47) buffer=63;// /
			else continue;
			bs = bc % 4 ? bs * 64 + buffer : buffer;
			if(bc++ % 4) output += String.fromCharCode(255 & bs >> (-2 * bc & 6));
		}
		return output;
	};
	Module.b64Dec=function(str){
		var s=typeof atob=="function"?atob(str):Module.b64Atob(str);
		var a=new Uint8Array(s.length);
		for(var i=0;i<s.length;i++)a[i]=s.charCodeAt(i);
		return a;
	};
    allocate(Module.b64Dec("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CQAUAFQAAQD+/wIAAwAGAAUACQAUAFQAAQD+/wIAAwAGAAUACQAUAFQAAQD+/wIAAwAGAAoAEwAUAFQAAQD+/wIAAwAGAAUACQAUAF4AAAD9/wMAAwAGAAUACQASAAAAAAAAAAAAAAAAAAAAAAAAABEAEwATABMAEwAXACcAOQAFAAgACAAHAAgABwACAAgABAAHAAIABAAHAAIACAAEAAcAAgAIAAgABwAIAAcAAgAGAAQABwACAAYABAAHAAIABgAEAAcAAgAGAAgACQAJAAgACQACAAYABAAJAAIABgAIAAkAAgAGAAQACQACAAYACAAJAAkACAALAAMABwAEAAsAAwAHAAgACwADAAcABAALAAMABwAIAAkACQAIAA0ABAAHAAUADQAEAAcACAANAAQABwAFAA0ABAAHAAkACQAJAAgADQAEAAQABQAGAA0ABAAEAAUACAANAAQABAAFAAYADQAEAAQABQAIAAkACQAIAAEAAQABAAEACgAKAAcABwAFAAEAAQABAAEACgAKAAcABwAIAAEAAQABAAEACgAKAAcABwAFAAEAAQABAAEACgAKAAcABwAHAAgACQAIAAYACQAEAAQABAAEAAQABAADAAMAAwADAAMABQAGAAQABAAEAAQABAAEAAMAAwADAAMAAwAFAAkABAAEAAQABAAEAAQAAwADAAMAAwADAAUABgAEAAQABAAEAAQABAADAAMAAwADAAMABQADAAgACQAJAAYAXwBnAHYAhgCUAJ8AzAD0ACcAKwAmACUAAAAAAAAAAAAAAAEAAgADAAQABQAGAAcACAAJAAoACwAMAA0ADgAPABcAGAAZABoAGwAcADAAMQA9AD4AUgBTAC8ALgAtACwAUQBQAE8ATgARABIAFAAWAE0ATABLAEoAHQAeACsAKgApACgAJgAnABAAEwAVADIAMwA7ADwAPwBAAEgASQBUAFUAXQBeACAAIQAjACQANQA2ADgAOQBCAEMARQBGAFcAWABaAFsAIgA3AEQAWQAlADoARwBcAB8ANABBAFYABwAGAAUABAADAAIAAQAAAA8ADgANAAwACwAKAAkACAAXABgAGQAaABsALgBBAFQALQAsACsAQAA/AD4AUwBSAFEAZgBlAGQAKgA9AFAAYwAcAC8AQgBVABIAKQA8AE8AYgAdADAAQwARABQAFgAoADsATgBhABUAHgAxAEQAVgATABAAVwAnACYAOgA5AE0AIwA2AEkAXABMAGAAXwAkADcASgBdACAAMwAhADQARgBHAFkAWgAfADIARQBYACUAOABLAF4AIgA1AEgAWwAAAAEABAAFAAMABgAHAAIADQAPAAgACQALAAwADgAKABAAHABKAB0ASwAbAEkAGgBIAB4ATAAzAGEAMgBHAGAAdQAfAE0ANABiADEARgBfAHQANQBjACAATgAhAE8AMABFAF4AcwAvAEQAXQByAC4AQwBcAHEAEwAVABcAFgASABEAFAAYAG8AKwBZAG4AQABBACwAWgAZAC0AQgBbAHAANgBkACgAPQBWAGsAJwA8AFUAagAkADkAUgBnACMAOABRAGYAIgA3AFAAZQAqAD8AWABtACkAPgBXAGwAJgA7AFQAaQAlADoAUwBoAAAAAQAEAAMABQAGAA0ABwACAAgACQALAA8ADAAOAAoAHABSAB0AUwAbAFEAGgBQAB4AVAAQADcAbQA4AG4AHwBVADkAbwAwAEkAZgB/ACAAVgAzAEwAaQCCADQATQBqAIMAOgBwACEAVwATABcANQBOAGsAhAAVABYAEgARABQAGAAZADIASwBoAIEALwBIAGUAfgA2AE8AbACFAC4ARwBkAH0AgABnAEoAMQAtAEYAYwB8ACoAQwBgAHkAJwBAAF0AdgAmAD8AXAB1ACMAPABZAHIAIgA7AFgAcQAsAEUAYgB7ACsARABhAHoAKQBCAF8AeAAoAEEAXgB3ACUAPgBbAHQAJAA9AFoAcwAAAAEAAgADAAQABQAGAAcACAAJAAoACwAMAA0ADgAPABAAGgBXABsAWAAcAFkAHQBaAB4AWwAzAFAAcACNADQAUQBxAI4ANgBTAHMAkAA3AFQAdACRADoAdwA7AHgAFQAWABcAEQASABMAHwA8AFwAeQA4AFUAdQCSABQAGAAZADIATwBvAIwAOQBWAHYAkwAxAE4AbgCLADAATQA1AFIAcgCPAG0AigAvAEwAbACJACAAIQA9AD4AXQBeAHoAewApACoAKwAsAC0ALgBGAEcASABJAEoASwBmAGcAaABpAGoAawCDAIQAhQCGAIcAiAAiAD8AXwB8ACMAQABgAH0AJABBAGEAfgAlAEIAYgB/ACYAQwBjAIAAJwBEAGQAgQAoAEUAZQCCAAgABwAGAAUABAADAAIADgAQAAkACgAMAA0ADwALABEAFAAWABgAFwATABIAFQA4AFgAegCaADkAWQB7AJsAOgBaAHwAnAA0AFQAdgCWADUAVQB3AJcAGwBdABwAXgAdAF8AHgBgAB8AYQA9AH8APgCAAD8AgQA7AFsAfQCdACAAYgBAAIIAAQAAABkAGgAhAGMAIgBkAEEAgwBCAIQANgBWAHgAmAA8AFwAfgCeADcAVwB5AJkAdQB0AHMALgBOAHAAkAArAEsAbQCNACgASABqAIoAJABEAGYAhgByAJUAlACTAJIAUwBSAFEAUAAzADIAMQAwAC8ALQAsACoAJwAjAE8ATQBMAEoARwBDAHEAbwBuAGwAaQBlAJEAjwCOAIwAiQCFACkASQBrAIsAJQBFAGcAhwAmAEYAaACIAAcABgAFAAQAAwACAAEAAAAQAA8ADgANAAwACwAKAAkACAAaABsAHAAdAB4AHwBzAHQAdQB2AHcAeABIAEkAoQCiAEEARABFAGwAbwBwAJoAnQCeAMUAyADJACAAIQB5AHoASgBLAKMApABCAG0AmwDGABMAFwAVABYAEgARABQAGAAZACUAJAAjACIAUABPAE4ATQB+AH0AfAB7AKkAqACnAKYARgBDAEcAcQBuAHIAnwCcAKAAygDHAMsATAClAFEAUgBcAFsAXQBTAF8AVQBUAF4AZQBmAGAAaABWAGcAVwBhAH8AgACKAIkAiwCBAI0AgwCCAIwAkwCUAI4AlgCEAJUAhQCPAKoAqwC1ALQAtgCsALgArgCtALcAvgC/ALkAwQCvAMAAsAC6ACYAJwAxADAAMgAoADQAKgApADMAOgA7ADUAPQArADwALAA2AMIAswC9AMQAsQDDALIAuwC8AJcAiACSAJkAhgCYAIcAkACRAGkAWgBkAGsAWABqAFkAYgBjAD4ALwA5AEAALQA/AC4ANwA4AAAAAQACAAMABAAFAAYABwAIAAkACgALAAwADQAOABcADwAQABEAEgATABQAFQAWABgAGQAaABsAHAAmAI0AJwCOACgAjwApAJAAKgCRACsAkgAsAJMALQCUAC4AlQAvAGEAlgDIADAAYgCXAMkAMQBjAJgAygBWAIgAvQDvAFcAiQC+APAAWACKAL8A8QBbAMIAXADDAF0AxABeAMUAXwDGAB0AHgAfACAAIQAiACMAMgBkAJkA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"), "i8", ALLOC_NONE, Runtime.GLOBAL_BASE);
    allocate(Module.b64Dec("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"), "i8", ALLOC_NONE, Runtime.GLOBAL_BASE + 10240);
    allocate(Module.b64Dec("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"), "i8", ALLOC_NONE, Runtime.GLOBAL_BASE + 20480);
    allocate(Module.b64Dec("anwhe6d5/Hcidhh033F6b+dsKWpBZy9k9WCVXQ9aZVaZUqtOnkp0Ri1CzD1SOcE0GzBiK5cmvSHVHOIX5hLiDdgIywM9CkAKSQpYCmwKhwqnCs0K+QorC2MLoAvjCywMegzPDCgNiA3tDVcOxw48D7cPNxC9EEcR1xFsEgYTpRNJFPIUnxVSFgkXxBeFGEkZEhrgGrEbhxxhHT4eIB8FIO4g2yHLIr8jtiSwJa4mriexKLgpwSrMK9os6y3+LhMwKjFDMl4zezSaNbo22zf+OCI6RzttPJQ9vD7kPw1BNkJgQ4pEtEXdRgdIMElZSoJLqUzQTfZOG1A/UWJShFOkVMJV31b6VxNZK1pAW1NcY11xXn1fhmCMYY9ikGONZIdlfmZyZ2JoT2k4ah5r/2vdbLdtjG5ebytw9HC5cXlyNXPsc550THX1dZl2N3fRd2Z49niBeQZ6hnoBe3Z75ntRfLZ8FX1vfcN9EX5afp1+234Sf0R/cH+Wf7d/0X/mf/R//X//f/9/9H/Qf5V/Qn/XflV+vH0MfUV8aHt1emx5Tngcd9V1enQNc4xx+m9XbqJs3moLaShnOWU8YzNhHl//XNdapVhsVixU5VGaT0pN90qhSEpG80OcQUc/9DykOlg4EjbRM5gxZy8+LR8rCykCJwUlFSMzIV8fmx3nG0MasRgxF8MVaRQiE+8R0RDJD9YO+Q0yDYIM6AtmC/wKqQptCkkKPQo9Cj8KQwpKClQKYApvCoEKlgquCsgK5QoFCycLTQt1C58LzQv9CzAMZQydDNgMFg1WDZkN3g0mDnEOvg4ND2APtQ8MEGYQwhAhEYIR5hFMErQSHxOME/wTbhTiFFgV0RVMFskWSBfKF00Y0xhbGeUZcRr+Go4bIBy0HEod4R17HhYfsx9SIPIglSE5It4ihSMuJNgkhCUyJuAmkSdCKPUoqSlfKhYrziuHLEIt/S26LngvNjD2MLcxeDI7M/4zwjSHNU02EzfaN6E4ajkyOvw6xTuQPFo9JT7wPrw/iEBUQSBC7EK5Q4VEUkUeRutGt0eESFBJHErnSrNLfkxJTRNO3U6mT29QOFEAUsdSjlNUVBlV3VWhVmRXJljnWKdZZ1olW+JbnlxZXRNezF6DXzlg7mCiYVRiBWO1Y2NkD2W6ZWRmDGeyZ1do+mibaTtq2Wp1axBsqGw/bdNtZm73boZvE3CecCdxrnEycrVyNXOzcy90qXQhdZZ1CXZ6duh2VHe+dyV4injseEx5qnkFel56tHoHe1h7p3vyezx8gnzGfAh9R32Dfbx9830nfll+iH60ft1+BH8of0l/Z3+Df5x/sn/Ff9Z/5H/vf/d//X//f/9/YX2gdQ9pMFi1Q3QsYhNEZWNvZGVyAGVuY29kZXIA"), "i8", ALLOC_NONE, Runtime.GLOBAL_BASE + 30720);
    var tempDoublePtr = Runtime.alignMemory(allocate(12, "i8", ALLOC_STATIC), 8);
    assert(tempDoublePtr % 8 == 0);

    //精简

    function _sbrk(bytes) {
        var self = _sbrk;
        if (!self.called) {
            DYNAMICTOP = alignMemoryPage(DYNAMICTOP);
            self.called = true;
            assert(Runtime.dynamicAlloc);
            self.alloc = Runtime.dynamicAlloc;
            Runtime.dynamicAlloc = (function () {
                abort("cannot dynamically allocate, sbrk now has control")
            })
        }
        var ret = DYNAMICTOP;
        if (bytes != 0) {
            var success = self.alloc(bytes);
            if (!success) return -1 >>> 0
        }
        return ret
    }

    function ___setErrNo(value) {
        if (Module["___errno_location"]) HEAP32[Module["___errno_location"]() >> 2] = value;
        return value
    }

    //精简

    function _sysconf(name) {
        if(name==30) return PAGE_SIZE;
        abort("fix _sysconf"); //精简
    }

    function _emscripten_memcpy_big(dest, src, num) {
        HEAPU8.set(HEAPU8.subarray(src, src + num), dest);
        return dest
    }

    Module["_memcpy"] = _memcpy;
    Module["_memmove"] = _memmove;
    Module["_memset"] = _memset;

	function abort(what) {
        throw new Error("abort(" + what + ")")
    }
	Module.abort = abort;
    function _abort(what) {
        Module["abort"](what)
    }

    //精简

    function _emscripten_set_main_loop_timing(mode, value) {
        //精简
    }

    function _emscripten_set_main_loop(func, fps, simulateInfiniteLoop, arg, noSetTiming) {
        //精简
    }

    //精简

    function _time(ptr) {
        var ret = Date.now() / 1e3 | 0;
        if (ptr) {
            HEAP32[ptr >> 2] = ret
        }
        return ret
    }

    function _pthread_self() {
        return 0
    }

    //精简

    STACK_BASE = STACKTOP = Runtime.alignMemory(STATICTOP);
    staticSealed = true;
    STACK_MAX = STACK_BASE + TOTAL_STACK;
    DYNAMIC_BASE = DYNAMICTOP = Runtime.alignMemory(STACK_MAX);
    assert(DYNAMIC_BASE < TOTAL_MEMORY, "TOTAL_MEMORY not big enough for stack");
    Module.asmGlobalArg = {
        "Math": Math,
        "Int8Array": Int8Array,
        "Int16Array": Int16Array,
        "Int32Array": Int32Array,
        "Uint8Array": Uint8Array,
        "Uint16Array": Uint16Array,
        "Uint32Array": Uint32Array,
        "Float32Array": Float32Array,
        "Float64Array": Float64Array,
        "NaN": NaN,
        "Infinity": Infinity
    };
    Module.asmLibraryArg = {
        "abort": abort,
        "assert": assert,
        "_sysconf": _sysconf,
        "_pthread_self": _pthread_self,
        "_abort": _abort,
        "___setErrNo": ___setErrNo,
        "_sbrk": _sbrk,
        "_time": _time,
        "_emscripten_set_main_loop_timing": _emscripten_set_main_loop_timing,
        "_emscripten_memcpy_big": _emscripten_memcpy_big,
        "_emscripten_set_main_loop": _emscripten_set_main_loop,
        "STACKTOP": STACKTOP,
        "STACK_MAX": STACK_MAX,
        "tempDoublePtr": tempDoublePtr,
        "ABORT": ABORT
    };// EMSCRIPTEN_START_ASM
    var asm = (function (global, env, buffer) {
        "use asm";
        var a = new global.Int8Array(buffer);
        var b = new global.Int16Array(buffer);
        var c = new global.Int32Array(buffer);
        var d = new global.Uint8Array(buffer);
        var e = new global.Uint16Array(buffer);
        var f = new global.Uint32Array(buffer);
        var g = new global.Float32Array(buffer);
        var h = new global.Float64Array(buffer);
        var i = env.STACKTOP | 0;
        var j = env.STACK_MAX | 0;
        var k = env.tempDoublePtr | 0;
        var l = env.ABORT | 0;
        var m = 0;
        var n = 0;
        var o = 0;
        var p = 0;
        var q = global.NaN, r = global.Infinity;
        var s = 0, t = 0, u = 0, v = 0, w = 0.0, x = 0, y = 0, z = 0, A = 0.0;
        var B = 0;
        var C = 0;
        var D = 0;
        var E = 0;
        var F = 0;
        var G = 0;
        var H = 0;
        var I = 0;
        var J = 0;
        var K = 0;
        var L = global.Math.floor;
        var M = global.Math.abs;
        var N = global.Math.sqrt;
        var O = global.Math.pow;
        var P = global.Math.cos;
        var Q = global.Math.sin;
        var R = global.Math.tan;
        var S = global.Math.acos;
        var T = global.Math.asin;
        var U = global.Math.atan;
        var V = global.Math.atan2;
        var W = global.Math.exp;
        var X = global.Math.log;
        var Y = global.Math.ceil;
        var Z = global.Math.imul;
        var _ = global.Math.min;
        var $ = global.Math.clz32;
        var aa = env.abort;
        var ba = env.assert;
        var ca = env._sysconf;
        var da = env._pthread_self;
        var ea = env._abort;
		var _abort=env._abort;
        var fa = env.___setErrNo;
        var ga = env._sbrk;
        var ha = env._time;
        var ia = env._emscripten_set_main_loop_timing;
        var ja = env._emscripten_memcpy_big;
        var ka = env._emscripten_set_main_loop;
        var la = 0.0;

// EMSCRIPTEN_START_FUNCS
        // 精简，这些函数不导出 不能留，不然压缩后会丢失参数类型

        function va() {
            var a = 0, b = 0;
            b = i;
            i = i + 16 | 0;
            a = b;
            c[a >> 2] = 0;
            Db(a, 31756) | 0;
            i = b;
            return c[a >> 2] | 0
        }

        function wa(a) {
            a = a | 0;
            var b = 0, d = 0;
            b = i;
            i = i + 16 | 0;
            d = b;
            c[d >> 2] = a;
            Eb(d);
            i = b;
            return
        }

        function xa(a, b, c, e) {
            a = a | 0;
            b = b | 0;
            c = c | 0;
            e = e | 0;
            Ea(a, (e | 0) == 0 ? (d[b >> 0] | 0) >>> 3 & 15 : 15, b + 1 | 0, c, 2) | 0;
            return
        }

        function ya(a) {
            a = a | 0;
            var b = 0;
            b = Je(8) | 0;
            Hb(b, b + 4 | 0, a) | 0;
            return b | 0
        }

        function za(a) {
            a = a | 0;
            Ib(a, a + 4 | 0);
            Ke(a);
            return
        }

        function Aa(b, e, f, g, h) {
            b = b | 0;
            e = e | 0;
            f = f | 0;
            g = g | 0;
            h = h | 0;
            var j = 0;
            h = i;
            i = i + 16 | 0;
            j = h;
            c[j >> 2] = e;
            f = (Jb(c[b >> 2] | 0, c[b + 4 >> 2] | 0, e, f, g, j, 3) | 0) << 16 >> 16;
            a[g >> 0] = d[g >> 0] | 0 | 4;
            i = h;
            return f | 0
        }

        function Ba(a) {
            a = a | 0;
            if (!a) a = -1; else {
                b[a >> 1] = 4096;
                a = 0
            }
            return a | 0
        }

        function Ca(a, d, e, f, g, h) {
            a = a | 0;
            d = d | 0;
            e = e | 0;
            f = f | 0;
            g = g | 0;
            h = h | 0;
            var i = 0, j = 0, k = 0, l = 0, m = 0, n = 0, o = 0, p = 0, q = 0;
            m = c[h >> 2] | 0;
            q = g << 16 >> 16 > 0;
            if (q) {
                i = 0;
                j = 0;
                do {
                    l = b[e + (i << 1) >> 1] | 0;
                    l = Z(l, l) | 0;
                    if ((l | 0) != 1073741824) {
                        k = (l << 1) + j | 0;
                        if ((l ^ j | 0) > 0 & (k ^ j | 0) < 0) {
                            c[h >> 2] = 1;
                            j = (j >>> 31) + 2147483647 | 0
                        } else j = k
                    } else {
                        c[h >> 2] = 1;
                        j = 2147483647
                    }
                    i = i + 1 | 0
                } while ((i & 65535) << 16 >> 16 != g << 16 >> 16);
                if ((j | 0) == 2147483647) {
                    c[h >> 2] = m;
                    l = 0;
                    k = 0;
                    do {
                        j = b[e + (l << 1) >> 1] >> 2;
                        j = Z(j, j) | 0;
                        if ((j | 0) != 1073741824) {
                            i = (j << 1) + k | 0;
                            if ((j ^ k | 0) > 0 & (i ^ k | 0) < 0) { //不可精简
                                c[h >> 2] = 1;
                                k = (k >>> 31) + 2147483647 | 0
                            } else k = i
                        } else {
                            c[h >> 2] = 1;
                            k = 2147483647
                        }
                        l = l + 1 | 0
                    } while ((l & 65535) << 16 >> 16 != g << 16 >> 16)
                } else p = 8
            } else {
                j = 0;
                p = 8
            }
            if ((p | 0) == 8) k = j >> 4;
            if (!k) {
                b[a >> 1] = 0;
                return
            }
            o = ((pe(k) | 0) & 65535) + 65535 | 0;
            j = o << 16 >> 16;
            if ((o & 65535) << 16 >> 16 > 0) {
                i = k << j;
                if ((i >> j | 0) == (k | 0)) k = i; else k = k >> 31 ^ 2147483647
            } else {
                j = 0 - j << 16;
                if ((j | 0) < 2031616) k = k >> (j >> 16); else k = 0
            }
            n = Ce(k, h) | 0;
            i = c[h >> 2] | 0;
            if (q) {
                j = 0;
                k = 0;
                do {
                    m = b[d + (j << 1) >> 1] | 0;
                    m = Z(m, m) | 0;
                    if ((m | 0) != 1073741824) {
                        l = (m << 1) + k | 0;
                        if ((m ^ k | 0) > 0 & (l ^ k | 0) < 0) {
                            c[h >> 2] = 1;
                            k = (k >>> 31) + 2147483647 | 0
                        } else k = l
                    } else {
                        c[h >> 2] = 1;
                        k = 2147483647
                    }
                    j = j + 1 | 0
                } while ((j & 65535) << 16 >> 16 != g << 16 >> 16);
                if ((k | 0) == 2147483647) {
                    c[h >> 2] = i;
                    m = 0;
                    k = 0;
                    do {
                        l = b[d + (m << 1) >> 1] >> 2;
                        l = Z(l, l) | 0;
                        if ((l | 0) != 1073741824) {
                            j = (l << 1) + k | 0;
                            if ((l ^ k | 0) > 0 & (j ^ k | 0) < 0) { //不可精简
                                c[h >> 2] = 1;
                                k = (k >>> 31) + 2147483647 | 0
                            } else k = j
                        } else {
                            c[h >> 2] = 1;
                            k = 2147483647
                        }
                        m = m + 1 | 0
                    } while ((m & 65535) << 16 >> 16 != g << 16 >> 16)
                } else p = 29
            } else {
                k = 0;
                p = 29
            }
            if ((p | 0) == 29) k = k >> 4;
            if (!k) l = 0; else {
                j = (pe(k) | 0) << 16 >> 16;
                i = o - j | 0;
                l = i & 65535;
                k = (Td(n, Ce(k << j, h) | 0) | 0) << 16 >> 16;
                j = k << 7;
                i = i << 16 >> 16;
                if (l << 16 >> 16 > 0) i = l << 16 >> 16 < 31 ? j >> i : 0; else {
                    p = 0 - i << 16 >> 16;
                    i = j << p;
                    i = (i >> p | 0) == (j | 0) ? i : k >> 24 ^ 2147483647
                }
                l = (Z(((ce(i, h) | 0) << 9) + 32768 >> 16, 32767 - (f & 65535) << 16 >> 16) | 0) >>> 15 << 16 >> 16
            }
            i = b[a >> 1] | 0;
            if (q) {
                k = f << 16 >> 16;
                j = 0;
                while (1) {
                    f = ((Z(i << 16 >> 16, k) | 0) >>> 15 & 65535) + l | 0;
                    i = f & 65535;
                    b[e >> 1] = (Z(b[e >> 1] | 0, f << 16 >> 16) | 0) >>> 12;
                    j = j + 1 << 16 >> 16;
                    if (j << 16 >> 16 >= g << 16 >> 16) break; else e = e + 2 | 0
                }
            }
            b[a >> 1] = i;
            return
        }

        function Da(a, d, e, f) {
            a = a | 0;
            d = d | 0;
            e = e | 0;
            f = f | 0;
            var g = 0, h = 0, i = 0, j = 0, k = 0, l = 0, m = 0, n = 0, o = 0;
            i = c[f >> 2] | 0;
            g = e << 16 >> 16 > 0;
            if (g) {
                j = 0;
                h = 0;
                do {
                    l = b[d + (j << 1) >> 1] | 0;
                    l = Z(l, l) | 0;
                    if ((l | 0) != 1073741824) {
                        k = (l << 1) + h | 0;
                        if ((l ^ h | 0) > 0 & (k ^ h | 0) < 0) {//不可精简
                            c[f >> 2] = 1;
                            h = (h >>> 31) + 2147483647 | 0
                        } else h = k
                    } else {
                        c[f >> 2] = 1;
                        h = 2147483647
                    }
                    j = j + 1 | 0
                } while ((j & 65535) << 16 >> 16 != e << 16 >> 16);
                if ((h | 0) == 2147483647) {//不可精简
                    c[f >> 2] = i;
                    l = 0;
                    i = 0;
                    do {
                        k = b[d + (l << 1) >> 1] >> 2;
                        k = Z(k, k) | 0;
                        if ((k | 0) != 1073741824) {
                            j = (k << 1) + i | 0;
                            if ((k ^ i | 0) > 0 & (j ^ i | 0) < 0) {
                                c[f >> 2] = 1;
                                i = (i >>> 31) + 2147483647 | 0
                            } else i = j
                        } else {
                            c[f >> 2] = 1;
                            i = 2147483647
                        }
                        l = l + 1 | 0
                    } while ((l & 65535) << 16 >> 16 != e << 16 >> 16)
                } else o = 8
            } else {
                h = 0;
                o = 8
            }
            if ((o | 0) == 8) i = h >> 4;
            if (!i) return;
            n = ((pe(i) | 0) & 65535) + 65535 | 0;
            k = n << 16 >> 16;
            if ((n & 65535) << 16 >> 16 > 0) {
                j = i << k;
                if ((j >> k | 0) == (i | 0)) i = j; else i = i >> 31 ^ 2147483647
            } else {
                k = 0 - k << 16;
                if ((k | 0) < 2031616) i = i >> (k >> 16); else i = 0
            }
            m = Ce(i, f) | 0;
            i = c[f >> 2] | 0;
            if (g) {
                j = 0;
                h = 0;
                do {
                    l = b[a + (j << 1) >> 1] | 0;
                    l = Z(l, l) | 0;
                    if ((l | 0) != 1073741824) {
                        k = (l << 1) + h | 0;
                        if ((l ^ h | 0) > 0 & (k ^ h | 0) < 0) {//不可精简
                            c[f >> 2] = 1;
                            h = (h >>> 31) + 2147483647 | 0
                        } else h = k
                    } else {
                        c[f >> 2] = 1;
                        h = 2147483647
                    }
                    j = j + 1 | 0
                } while ((j & 65535) << 16 >> 16 != e << 16 >> 16);
                if ((h | 0) == 2147483647) {//不可精简
                    c[f >> 2] = i;
                    i = 0;
                    j = 0;
                    do {
                        l = b[a + (i << 1) >> 1] >> 2;
                        l = Z(l, l) | 0;
                        if ((l | 0) != 1073741824) {
                            k = (l << 1) + j | 0;
                            if ((l ^ j | 0) > 0 & (k ^ j | 0) < 0) {
                                c[f >> 2] = 1;
                                j = (j >>> 31) + 2147483647 | 0
                            } else j = k
                        } else {
                            c[f >> 2] = 1;
                            j = 2147483647
                        }
                        i = i + 1 | 0
                    } while ((i & 65535) << 16 >> 16 != e << 16 >> 16)
                } else o = 28
            } else {
                h = 0;
                o = 28
            }
            if ((o | 0) == 28) j = h >> 4;
            if (!j) g = 0; else {
                l = pe(j) | 0;
                k = l << 16 >> 16;
                if (l << 16 >> 16 > 0) {
                    i = j << k;
                    if ((i >> k | 0) == (j | 0)) j = i; else j = j >> 31 ^ 2147483647
                } else {//不可精简
                    k = 0 - k << 16;
                    if ((k | 0) < 2031616) j = j >> (k >> 16); else j = 0
                }
                i = n - (l & 65535) | 0;
                k = i & 65535;
                h = (Td(m, Ce(j, f) | 0) | 0) << 16 >> 16;
                g = h << 7;
                i = i << 16 >> 16;
                if (k << 16 >> 16 > 0) g = k << 16 >> 16 < 31 ? g >> i : 0; else {
                    n = 0 - i << 16 >> 16;
                    a = g << n;
                    g = (a >> n | 0) == (g | 0) ? a : h >> 24 ^ 2147483647
                }
                g = ce(g, f) | 0;
                if ((g | 0) > 4194303) g = 2147483647; else g = (g | 0) < -4194304 ? -2147483648 : g << 9;
                g = Ce(g, f) | 0
            }
            h = (e & 65535) + 65535 & 65535;
            if (h << 16 >> 16 <= -1) return;
            l = g << 16 >> 16;
            k = e + -1 << 16 >> 16 << 16 >> 16;
            while (1) {
                i = d + (k << 1) | 0;
                g = Z(b[i >> 1] | 0, l) | 0;
                do if ((g | 0) != 1073741824) {
                    j = g << 1;
                    if ((j | 0) <= 268435455) if ((j | 0) < -268435456) {
                        b[i >> 1] = -32768;
                        break
                    } else {
                        b[i >> 1] = g >>> 12;
                        break
                    } else o = 52
                } else {
                    c[f >> 2] = 1;
                    o = 52
                } while (0);
                if ((o | 0) == 52) {
                    o = 0;
                    b[i >> 1] = 32767
                }
                h = h + -1 << 16 >> 16;
                if (h << 16 >> 16 <= -1) break; else k = k + -1 | 0
            }
            return
        }

        function Ea(a, d, e, f, g) {
            a = a | 0;
            d = d | 0;
            e = e | 0;
            f = f | 0;
            g = g | 0;
            var h = 0, j = 0, k = 0, l = 0;
            l = i;
            i = i + 496 | 0;
            k = l;
            j = (g | 0) == 2;
            do if (!(j & 1 | (g | 0) == 4)) {
                _abort();//fix cc 精简
            } else {
                h = a + 1168 | 0;
                if (j) {
                    Gb(d, e, k, h);
                    h = 604
                } else {
                    _abort();//fix cc 精简
                    
                }
                g = b[h + (d << 1) >> 1] | 0;
                do if (d >>> 0 >= 8) {
                    _abort();//fix cc 精简
                } else h = 0; while (0);
                if (g << 16 >> 16 == -1) {
                    a = -1;
                    i = l;
                    return a | 0
                }
            } while (0);
            Fb(a, d, k, h, f);
            c[a + 1760 >> 2] = d;
            a = g;
            i = l;
            return a | 0
        }

        //fix cc 精简

        function Ja(a) {
            a = a | 0;
            var c = 0;
            if (!a) {
                c = -1;
                return c | 0
            }
            c = a + 122 | 0;
            do {
                b[a >> 1] = 0;
                a = a + 2 | 0
            } while ((a | 0) < (c | 0));
            c = 0;
            return c | 0
        }

        function Ka(a, d, f, g, h) {
            a = a | 0;
            d = d | 0;
            f = f | 0;
            g = g | 0;
            h = h | 0;
            var i = 0, j = 0, k = 0, l = 0, m = 0, n = 0, o = 0;
            k = 159;
            j = 0;
            while (1) {
                m = b[f + (k << 1) >> 1] | 0;
                m = Z(m, m) | 0;
                m = (m | 0) == 1073741824 ? 2147483647 : m << 1;
                i = m + j | 0;
                if ((m ^ j | 0) > -1 & (i ^ j | 0) < 0) {
                    c[h >> 2] = 1;
                    j = (j >>> 31) + 2147483647 | 0
                } else j = i;
                if ((k | 0) > 0) k = k + -1 | 0; else {
                    k = j;
                    break
                }
            }
            h = k >>> 14 & 65535;
            j = 32767;
            i = 59;
            while (1) {
                m = b[a + (i << 1) >> 1] | 0;
                j = m << 16 >> 16 < j << 16 >> 16 ? m : j;
                if ((i | 0) > 0) i = i + -1 | 0; else break
            }
            m = (k | 0) > 536870911 ? 32767 : h;
            h = j << 16 >> 16;
            i = h << 20 >> 16;
            k = j << 16 >> 16 > 0 ? 32767 : -32768;
            f = 55;
            j = b[a >> 1] | 0;
            while (1) {
                l = b[a + (f << 1) >> 1] | 0;
                j = j << 16 >> 16 < l << 16 >> 16 ? l : j;
                if ((f | 0) > 1) f = f + -1 | 0; else break
            }
            f = b[a + 80 >> 1] | 0;
            l = b[a + 82 >> 1] | 0;
            f = f << 16 >> 16 < l << 16 >> 16 ? l : f;
            l = b[a + 84 >> 1] | 0;
            f = f << 16 >> 16 < l << 16 >> 16 ? l : f;
            l = b[a + 86 >> 1] | 0;
            f = f << 16 >> 16 < l << 16 >> 16 ? l : f;
            l = b[a + 88 >> 1] | 0;
            f = f << 16 >> 16 < l << 16 >> 16 ? l : f;
            l = b[a + 90 >> 1] | 0;
            f = f << 16 >> 16 < l << 16 >> 16 ? l : f;
            l = b[a + 92 >> 1] | 0;
            f = f << 16 >> 16 < l << 16 >> 16 ? l : f;
            l = b[a + 94 >> 1] | 0;
            f = f << 16 >> 16 < l << 16 >> 16 ? l : f;
            l = b[a + 96 >> 1] | 0;
            f = f << 16 >> 16 < l << 16 >> 16 ? l : f;
            l = b[a + 98 >> 1] | 0;
            f = f << 16 >> 16 < l << 16 >> 16 ? l : f;
            l = b[a + 100 >> 1] | 0;
            f = f << 16 >> 16 < l << 16 >> 16 ? l : f;
            l = b[a + 102 >> 1] | 0;
            f = f << 16 >> 16 < l << 16 >> 16 ? l : f;
            l = b[a + 104 >> 1] | 0;
            f = f << 16 >> 16 < l << 16 >> 16 ? l : f;
            l = b[a + 106 >> 1] | 0;
            f = f << 16 >> 16 < l << 16 >> 16 ? l : f;
            l = b[a + 108 >> 1] | 0;
            f = f << 16 >> 16 < l << 16 >> 16 ? l : f;
            l = b[a + 110 >> 1] | 0;
            f = f << 16 >> 16 < l << 16 >> 16 ? l : f;
            l = b[a + 112 >> 1] | 0;
            f = f << 16 >> 16 < l << 16 >> 16 ? l : f;
            l = b[a + 114 >> 1] | 0;
            f = f << 16 >> 16 < l << 16 >> 16 ? l : f;
            l = b[a + 116 >> 1] | 0;
            f = f << 16 >> 16 < l << 16 >> 16 ? l : f;
            l = a + 118 | 0;
            o = b[l >> 1] | 0;
            do if ((m + -21 & 65535) < 17557 & j << 16 >> 16 > 20 ? ((m << 16 >> 16 | 0) < (((h << 4 | 0) == (i | 0) ? i : k) | 0) ? 1 : (f << 16 >> 16 < o << 16 >> 16 ? o : f) << 16 >> 16 < 1953) : 0) {
                j = a + 120 | 0;
                i = b[j >> 1] | 0;
                if (i << 16 >> 16 > 29) {//不可精简
                    b[j >> 1] = 30;
                    f = j;
                    k = 1;
                    break
                } else {
                    k = (i & 65535) + 1 & 65535;
                    b[j >> 1] = k;
                    f = j;
                    k = k << 16 >> 16 > 1 & 1;
                    break
                }
            } else n = 14; while (0);
            if ((n | 0) == 14) {
                f = a + 120 | 0;
                b[f >> 1] = 0;
                k = 0
            }
            j = 0;
            do {
                o = j;
                j = j + 1 | 0;
                b[a + (o << 1) >> 1] = b[a + (j << 1) >> 1] | 0
            } while ((j | 0) != 59);
            b[l >> 1] = m;
            j = b[f >> 1] | 0;
            j = j << 16 >> 16 > 15 ? 16383 : j << 16 >> 16 > 8 ? 15565 : 13926;
            i = Zd(d + 8 | 0, 5) | 0;
            if ((b[f >> 1] | 0) > 20) {
                if (((Zd(d, 9) | 0) << 16 >> 16 | 0) > (j | 0)) n = 20
            } else if ((i << 16 >> 16 | 0) > (j | 0)) n = 20;
            if ((n | 0) == 20) {
                b[g >> 1] = 0;
                return k | 0
            }
            i = (e[g >> 1] | 0) + 1 & 65535;
            if (i << 16 >> 16 > 10) {
                b[g >> 1] = 10;
                return k | 0
            } else {
                b[g >> 1] = i;
                return k | 0
            }
            return 0
        }

        function La(a) {
            a = a | 0;
            var c = 0;
            if (!a) {
                c = -1;
                return c | 0
            }
            c = a + 18 | 0;
            do {
                b[a >> 1] = 0;
                a = a + 2 | 0
            } while ((a | 0) < (c | 0));
            c = 0;
            return c | 0
        }

        function Ma(a, d, f, g, h, i, j, k, l, m, n, o) {
            a = a | 0;
            d = d | 0;
            f = f | 0;
            g = g | 0;
            h = h | 0;
            i = i | 0;
            j = j | 0;
            k = k | 0;
            l = l | 0;
            m = m | 0;
            n = n | 0;
            o = o | 0;
            var p = 0, q = 0, r = 0, s = 0, t = 0, u = 0, v = 0, w = 0, x = 0, y = 0, z = 0, A = 0, B = 0, C = 0, D = 0;
            y = a + 2 | 0;
            b[a >> 1] = b[y >> 1] | 0;
            z = a + 4 | 0;
            b[y >> 1] = b[z >> 1] | 0;
            A = a + 6 | 0;
            b[z >> 1] = b[A >> 1] | 0;
            B = a + 8 | 0;
            b[A >> 1] = b[B >> 1] | 0;
            C = a + 10 | 0;
            b[B >> 1] = b[C >> 1] | 0;
            D = a + 12 | 0;
            b[C >> 1] = b[D >> 1] | 0;
            b[D >> 1] = f;
            t = 0;
            x = 0;
            do {
                p = h + (x << 1) | 0;
                r = Ge(b[p >> 1] | 0, b[g + (x << 1) >> 1] | 0, o) | 0;
                r = (r & 65535) - ((r & 65535) >>> 15 & 65535) | 0;
                r = r << 16 >> 31 ^ r;
                w = ((qe(r & 65535) | 0) & 65535) + 65535 | 0;
                q = w << 16 >> 16;
                if ((w & 65535) << 16 >> 16 < 0) {
                    s = 0 - q << 16;
                    if ((s | 0) < 983040) u = r << 16 >> 16 >> (s >> 16) & 65535; else u = 0
                } else {
                    s = r << 16 >> 16;
                    r = s << q;
                    if ((r << 16 >> 16 >> q | 0) == (s | 0)) u = r & 65535; else u = (s >>> 15 ^ 32767) & 65535
                }
                v = qe(b[p >> 1] | 0) | 0;
                r = b[p >> 1] | 0;
                q = v << 16 >> 16;
                if (v << 16 >> 16 < 0) {
                    _abort();//fix cc 精简
                } else {
                    s = r << 16 >> 16;
                    r = s << q;
                    if ((r << 16 >> 16 >> q | 0) == (s | 0)) s = r & 65535; else s = (s >>> 15 ^ 32767) & 65535
                }
                q = Td(u, s) | 0;
                s = (w & 65535) + 2 - (v & 65535) | 0;
                r = s & 65535;
                do if (s & 32768) {
                    if (r << 16 >> 16 != -32768) {
                        w = 0 - s | 0;
                        s = w << 16 >> 16;
                        if ((w & 65535) << 16 >> 16 < 0) {
                            _abort();//fix cc 精简
                        }
                    } else s = 32767;
                    r = q << 16 >> 16;
                    q = r << s;
                    if ((q << 16 >> 16 >> s | 0) == (r | 0)) s = q & 65535; else s = (r >>> 15 ^ 32767) & 65535
                } else s = De(q, r, o) | 0; while (0);
                t = Rd(t, s, o) | 0;
                x = x + 1 | 0
            } while ((x | 0) != 10);
            s = t & 65535;
            r = t << 16 >> 16 > 5325;
            t = a + 14 | 0;
            if (r) {
                h = (e[t >> 1] | 0) + 1 & 65535;
                b[t >> 1] = h;
                if (h << 16 >> 16 > 10) b[a + 16 >> 1] = 0
            } else b[t >> 1] = 0;
            switch (d | 0) {
                case 0:
                case 1:
                case 2:
                case 3:
                case 6:
                    break;
                default: {
                    D = a + 16 | 0;
                    o = f;
                    f = b[D >> 1] | 0;
                    f = f & 65535;
                    f = f + 1 | 0;
                    f = f & 65535;
                    b[D >> 1] = f;
                    return o | 0
                }
            }
            u = (j | i) << 16 >> 16 == 0;
            v = m << 16 >> 16 == 0;
            w = d >>> 0 < 3;
            t = s + (w & ((v | (u & (k << 16 >> 16 == 0 | l << 16 >> 16 == 0) | n << 16 >> 16 < 2)) ^ 1) ? 61030 : 62259) & 65535;
            t = t << 16 >> 16 > 0 ? t : 0;
            if (t << 16 >> 16 <= 2048) {
                t = t << 16 >> 16;
                if ((t << 18 >> 18 | 0) == (t | 0)) l = t << 2; else l = t >>> 15 ^ 32767
            } else l = 8192;
            k = a + 16 | 0;
            n = r | (b[k >> 1] | 0) < 40;
            t = b[z >> 1] | 0;
            if ((t * 6554 | 0) == 1073741824) {
                c[o >> 2] = 1;
                r = 2147483647
            } else r = t * 13108 | 0;
            t = b[A >> 1] | 0;
            s = t * 6554 | 0;
            if ((s | 0) != 1073741824) {
                t = (t * 13108 | 0) + r | 0;
                if ((s ^ r | 0) > 0 & (t ^ r | 0) < 0) {
                    c[o >> 2] = 1;
                    t = (r >>> 31) + 2147483647 | 0
                }
            } else {
                c[o >> 2] = 1;
                t = 2147483647
            }
            s = b[B >> 1] | 0;
            r = s * 6554 | 0;
            if ((r | 0) != 1073741824) {
                s = (s * 13108 | 0) + t | 0;
                if ((r ^ t | 0) > 0 & (s ^ t | 0) < 0) {
                    c[o >> 2] = 1;
                    s = (t >>> 31) + 2147483647 | 0
                }
            } else {
                c[o >> 2] = 1;
                s = 2147483647
            }
            t = b[C >> 1] | 0;
            r = t * 6554 | 0;
            if ((r | 0) != 1073741824) {
                t = (t * 13108 | 0) + s | 0;
                if ((r ^ s | 0) > 0 & (t ^ s | 0) < 0) {
                    c[o >> 2] = 1;
                    r = (s >>> 31) + 2147483647 | 0
                } else r = t
            } else {
                c[o >> 2] = 1;
                r = 2147483647
            }
            t = b[D >> 1] | 0;
            s = t * 6554 | 0;
            if ((s | 0) != 1073741824) {
                t = (t * 13108 | 0) + r | 0;
                if ((s ^ r | 0) > 0 & (t ^ r | 0) < 0) {
                    c[o >> 2] = 1;
                    t = (r >>> 31) + 2147483647 | 0
                }
            } else {
                c[o >> 2] = 1;
                t = 2147483647
            }
            r = Ce(t, o) | 0;
            if (w & ((u | v) ^ 1)) {
                _abort();//fix cc 精简
            }
            t = n ? 8192 : l << 16 >> 16;
            p = Z(t, f << 16 >> 16) | 0;
            if ((p | 0) == 1073741824) {
                c[o >> 2] = 1;
                s = 2147483647
            } else s = p << 1;
            r = r << 16 >> 16;
            q = r << 13;
            if ((q | 0) != 1073741824) {
                p = s + (r << 14) | 0;
                if ((s ^ q | 0) > 0 & (p ^ s | 0) < 0) {
                    c[o >> 2] = 1;
                    s = (s >>> 31) + 2147483647 | 0
                } else s = p
            } else {
                c[o >> 2] = 1;
                s = 2147483647
            }
            p = Z(r, t) | 0;
            if ((p | 0) == 1073741824) {
                c[o >> 2] = 1;
                q = 2147483647
            } else q = p << 1;
            p = s - q | 0;
            if (((p ^ s) & (q ^ s) | 0) < 0) {
                c[o >> 2] = 1;
                p = (s >>> 31) + 2147483647 | 0
            }
            D = p << 2;
            f = k;
            o = Ce((D >> 2 | 0) == (p | 0) ? D : p >> 31 ^ 2147483647, o) | 0;
            D = b[f >> 1] | 0;
            D = D & 65535;
            D = D + 1 | 0;
            D = D & 65535;
            b[f >> 1] = D;
            return o | 0
        }

        function Na(a, c, d) {
            a = a | 0;
            c = c | 0;
            d = d | 0;
            var f = 0, g = 0, h = 0, i = 0;
            f = c;
            g = f + 80 | 0;
            do {
                b[f >> 1] = 0;
                f = f + 2 | 0
            } while ((f | 0) < (g | 0));
            f = 0;
            do {
                i = b[a + (f << 1) >> 1] | 0;
                g = ((i & 8) << 10 & 65535 ^ 8192) + -4096 << 16 >> 16;
                h = f << 16;
                i = ((b[d + ((i & 7) << 1) >> 1] | 0) * 327680 | 0) + h >> 16;
                b[c + (i << 1) >> 1] = g;
                h = ((b[d + ((e[a + (f + 5 << 1) >> 1] & 7) << 1) >> 1] | 0) * 327680 | 0) + h >> 16;
                if ((h | 0) < (i | 0)) g = 0 - (g & 65535) & 65535;
                i = c + (h << 1) | 0;
                b[i >> 1] = (e[i >> 1] | 0) + (g & 65535);
                f = f + 1 | 0
            } while ((f | 0) != 5);
            return
        }

        function Oa(a, c, d) {
            a = a | 0;
            c = c | 0;
            d = d | 0;
            var e = 0, f = 0, g = 0;
            f = c << 16 >> 16;
            e = (f << 1 & 2 | 1) + ((f >>> 1 & 7) * 5 | 0) | 0;
            c = f >>> 4 & 3;
            c = ((f >>> 6 & 7) * 5 | 0) + ((c | 0) == 3 ? 4 : c) | 0;
            f = d;
            g = f + 80 | 0;
            do {
                b[f >> 1] = 0;
                f = f + 2 | 0
            } while ((f | 0) < (g | 0));
            a = a << 16 >> 16;
            b[d + (e << 1) >> 1] = (0 - (a & 1) & 16383) + 57344;
            b[d + (c << 1) >> 1] = (0 - (a >>> 1 & 1) & 16383) + 57344;
            return
        }

        function Pa(a, c, d, f, g, h) {
            a = a | 0;
            c = c | 0;
            d = d | 0;
            f = f | 0;
            g = g | 0;
            h = h | 0;
            var i = 0, j = 0;
            h = d << 16 >> 16;
            j = h >>> 3;
            a = a << 16 >> 16;
            a = ((a << 17 >> 17 | 0) == (a | 0) ? a << 1 : a >>> 15 ^ 32767) + (j & 8) << 16;
            j = (e[f + (a + 65536 >> 16 << 1) >> 1] | 0) + ((j & 7) * 5 | 0) | 0;
            d = c << 16 >> 16;
            i = (0 - (d & 1) & 16383) + 57344 & 65535;
            a = g + ((e[f + (a >> 16 << 1) >> 1] | 0) + ((h & 7) * 5 | 0) << 16 >> 16 << 1) | 0;
            c = g;
            h = c + 80 | 0;
            do {
                b[c >> 1] = 0;
                c = c + 2 | 0
            } while ((c | 0) < (h | 0));
            b[a >> 1] = i;
            b[g + (j << 16 >> 16 << 1) >> 1] = (0 - (d >>> 1 & 1) & 16383) + 57344;
            return
        }

        function Qa(a, c, d) {
            a = a | 0;
            c = c | 0;
            d = d | 0;
            var e = 0, f = 0, g = 0, h = 0;
            c = c << 16 >> 16;
            e = (c & 7) * 5 | 0;
            f = (c >>> 2 & 2 | 1) + ((c >>> 4 & 7) * 5 | 0) | 0;
            c = (c >>> 6 & 2) + 2 + ((c >>> 8 & 7) * 5 | 0) | 0;
            g = d;
            h = g + 80 | 0;
            do {
                b[g >> 1] = 0;
                g = g + 2 | 0
            } while ((g | 0) < (h | 0));
            a = a << 16 >> 16;
            b[d + (e << 1) >> 1] = (0 - (a & 1) & 16383) + 57344;
            b[d + (f << 1) >> 1] = (0 - (a >>> 1 & 1) & 16383) + 57344;
            b[d + (c << 1) >> 1] = (0 - (a >>> 2 & 1) & 16383) + 57344;
            return
        }

        function Ra(a, c, d, e) {
            a = a | 0;
            c = c | 0;
            d = d | 0;
            e = e | 0;
            var f = 0, g = 0, h = 0, i = 0;
            c = c << 16 >> 16;
            h = b[d + ((c & 7) << 1) >> 1] | 0;
            i = b[d + ((c >>> 3 & 7) << 1) >> 1] | 0;
            g = b[d + ((c >>> 6 & 7) << 1) >> 1] | 0;
            d = (c >>> 9 & 1) + 3 + ((b[d + ((c >>> 10 & 7) << 1) >> 1] | 0) * 5 | 0) | 0;
            c = e;
            f = c + 80 | 0;
            do {
                b[c >> 1] = 0;
                c = c + 2 | 0
            } while ((c | 0) < (f | 0));
            a = a << 16 >> 16;
            b[e + (h * 327680 >> 16 << 1) >> 1] = (0 - (a & 1) & 16383) + 57344;
            b[e + ((i * 327680 | 0) + 65536 >> 16 << 1) >> 1] = (0 - (a >>> 1 & 1) & 16383) + 57344;
            b[e + ((g * 327680 | 0) + 131072 >> 16 << 1) >> 1] = (0 - (a >>> 2 & 1) & 16383) + 57344;
            b[e + (d << 16 >> 16 << 1) >> 1] = (0 - (a >>> 3 & 1) & 16383) + 57344;
            return
        }

        function Sa(a, d, f) {
            a = a | 0;
            d = d | 0;
            f = f | 0;
            var g = 0, h = 0, j = 0, k = 0, l = 0, m = 0, n = 0, o = 0, p = 0, q = 0;
            q = i;
            i = i + 32 | 0;
            p = q + 16 | 0;
            o = q;
            j = d;
            h = j + 80 | 0;
            do {
                b[j >> 1] = 0;
                j = j + 2 | 0
            } while ((j | 0) < (h | 0));
            h = b[a >> 1] | 0;
            b[p >> 1] = h;
            b[p + 2 >> 1] = b[a + 2 >> 1] | 0;
            b[p + 4 >> 1] = b[a + 4 >> 1] | 0;
            b[p + 6 >> 1] = b[a + 6 >> 1] | 0;
            m = b[a + 8 >> 1] | 0;
            Ta(m >>> 3 & 65535, m & 7, 0, 4, 1, o, f);
            m = b[a + 10 >> 1] | 0;
            Ta(m >>> 3 & 65535, m & 7, 2, 6, 5, o, f);
            m = b[a + 12 >> 1] | 0;
            g = m >> 2;
            do if ((g * 25 | 0) != 1073741824) {
                j = (Z(g, 1638400) | 0) + 786432 >> 21;
                g = j * 6554 >> 15;
                if ((g | 0) > 32767) {
                    _abort();//fix cc 精简
                }
                a = (g << 16 >> 16) * 5 | 0;
                k = g & 1;
                if ((a | 0) == 1073741824) {
                    c[f >> 2] = 1;
                    l = 0;
                    a = 65535
                } else {
                    l = 0;
                    n = 6
                }
            } else {
                _abort();//fix cc 精简
            } while (0);
            if ((n | 0) == 6) a = a & 65535;
            n = j - a | 0;
            k = k << 16 >> 16 == 0 ? n : 4 - n | 0;
            n = k << 16 >> 16;
            b[o + 6 >> 1] = Rd(((k << 17 >> 17 | 0) == (n | 0) ? k << 1 : n >>> 15 ^ 32767) & 65535, m & 1, f) | 0;
            if (l) {
                c[f >> 2] = 1;
                g = 32767
            }
            n = g << 16 >> 16;
            b[o + 14 >> 1] = ((g << 17 >> 17 | 0) == (n | 0) ? g << 1 : n >>> 15 ^ 32767) + (m >>> 1 & 1);
            g = 0;
            while (1) {
                h = h << 16 >> 16 == 0 ? 8191 : -8191;
                n = (b[o + (g << 1) >> 1] << 2) + g << 16;
                j = n >> 16;
                if ((n | 0) < 2621440) b[d + (j << 1) >> 1] = h;
                k = (b[o + (g + 4 << 1) >> 1] << 2) + g << 16;
                a = k >> 16;
                if ((a | 0) < (j | 0)) h = 0 - (h & 65535) & 65535;
                if ((k | 0) < 2621440) {
                    n = d + (a << 1) | 0;
                    b[n >> 1] = (e[n >> 1] | 0) + (h & 65535)
                }
                g = g + 1 | 0;
                if ((g | 0) == 4) break;
                h = b[p + (g << 1) >> 1] | 0
            }
            i = q;
            return
        }

        function Ta(a, d, e, f, g, h, i) {
            a = a | 0;
            d = d | 0;
            e = e | 0;
            f = f | 0;
            g = g | 0;
            h = h | 0;
            i = i | 0;
            var j = 0, k = 0, l = 0, m = 0, n = 0, o = 0, p = 0;
            k = a << 16 >> 16 > 124 ? 124 : a;
            a = (k << 16 >> 16) * 1311 >> 15;
            p = (a | 0) > 32767;
            if (!p) {
                j = a << 16 >> 16;
                if ((j * 25 | 0) == 1073741824) {
                    c[i >> 2] = 1;
                    j = 1073741823
                } else o = 4
            } else {
                c[i >> 2] = 1;
                j = 32767;
                o = 4
            }
            if ((o | 0) == 4) j = (j * 50 | 0) >>> 1;
            m = (k & 65535) - j | 0;
            j = (m << 16 >> 16) * 6554 >> 15;
            n = (j | 0) > 32767;
            if (!n) {
                k = j << 16 >> 16;
                if ((k * 5 | 0) == 1073741824) {
                    c[i >> 2] = 1;
                    l = 1073741823
                } else o = 9
            } else {
                c[i >> 2] = 1;
                k = 32767;
                o = 9
            }
            if ((o | 0) == 9) l = (k * 10 | 0) >>> 1;
            m = m - l | 0;
            o = m << 16 >> 16;
            k = d << 16 >> 16;
            l = k >> 2;
            k = k - (l << 2) | 0;
            b[h + (e << 16 >> 16 << 1) >> 1] = ((m << 17 >> 17 | 0) == (o | 0) ? m << 1 : o >>> 15 ^ 32767) + (k & 1);
            if (n) {
                c[i >> 2] = 1;
                j = 32767
            }
            e = j << 16 >> 16;
            b[h + (f << 16 >> 16 << 1) >> 1] = ((j << 17 >> 17 | 0) == (e | 0) ? j << 1 : e >>> 15 ^ 32767) + (k << 16 >> 17);
            if (p) {
                c[i >> 2] = 1;
                a = 32767
            }
            f = a << 16 >> 16;
            b[h + (g << 16 >> 16 << 1) >> 1] = Rd(l & 65535, ((a << 17 >> 17 | 0) == (f | 0) ? a << 1 : f >>> 15 ^ 32767) & 65535, i) | 0;
            return
        }

        function Ua(a) {
            a = a | 0;
            var d = 0, e = 0, f = 0, g = 0;
            if (!a) {
                g = -1;
                return g | 0
            }
            Yd(a + 1168 | 0);
            b[a + 460 >> 1] = 40;
            c[a + 1164 >> 2] = 0;
            d = a + 646 | 0;
            e = a + 1216 | 0;
            f = a + 462 | 0;
            g = f + 22 | 0;
            do {
                b[f >> 1] = 0;
                f = f + 2 | 0
            } while ((f | 0) < (g | 0));
            db(d, c[e >> 2] | 0) | 0;
            mb(a + 686 | 0) | 0;
            ib(a + 700 | 0) | 0;
            La(a + 608 | 0) | 0;
            rb(a + 626 | 0, c[e >> 2] | 0) | 0;
            Ja(a + 484 | 0) | 0;
            tb(a + 730 | 0) | 0;
            eb(a + 748 | 0) | 0;
            Ud(a + 714 | 0) | 0;
            Va(a, 0) | 0;
            g = 0;
            return g | 0
        }

        function Va(a, d) {
            a = a | 0;
            d = d | 0;
            var e = 0, f = 0;
            if (!a) {
                a = -1;
                return a | 0
            }
            c[a + 388 >> 2] = a + 308;
            Qe(a | 0, 0, 308) | 0;
            d = (d | 0) != 8;
            if (d) {
                e = a + 412 | 0;
                f = e + 20 | 0;
                do {
                    b[e >> 1] = 0;
                    e = e + 2 | 0
                } while ((e | 0) < (f | 0));
                b[a + 392 >> 1] = 3e4;
                b[a + 394 >> 1] = 26e3;
                b[a + 396 >> 1] = 21e3;
                b[a + 398 >> 1] = 15e3;
                b[a + 400 >> 1] = 8e3;
                b[a + 402 >> 1] = 0;
                b[a + 404 >> 1] = -8e3;
                b[a + 406 >> 1] = -15e3;
                b[a + 408 >> 1] = -21e3;
                b[a + 410 >> 1] = -26e3
            }
            b[a + 432 >> 1] = 0;
            b[a + 434 >> 1] = 40;
            c[a + 1164 >> 2] = 0;
            b[a + 436 >> 1] = 0;
            b[a + 438 >> 1] = 0;
            b[a + 440 >> 1] = 0;
            b[a + 460 >> 1] = 40;
            b[a + 462 >> 1] = 0;
            b[a + 464 >> 1] = 0;
            if (d) {
                e = a + 442 | 0;
                f = e + 18 | 0;
                do {
                    b[e >> 1] = 0;
                    e = e + 2 | 0
                } while ((e | 0) < (f | 0));
                e = a + 466 | 0;
                f = e + 18 | 0;
                do {
                    b[e >> 1] = 0;
                    e = e + 2 | 0
                } while ((e | 0) < (f | 0));
                La(a + 608 | 0) | 0;
                f = a + 1216 | 0;
                rb(a + 626 | 0, c[f >> 2] | 0) | 0;
                db(a + 646 | 0, c[f >> 2] | 0) | 0;
                mb(a + 686 | 0) | 0;
                ib(a + 700 | 0) | 0;
                Ud(a + 714 | 0) | 0
            } else {
                _abort();//fix cc 精简
            }
            Ja(a + 484 | 0) | 0;
            b[a + 606 >> 1] = 21845;
            tb(a + 730 | 0) | 0;
            if (!d) {
                a = 0;
                return a | 0
            }
            eb(a + 748 | 0) | 0;
            a = 0;
            return a | 0
        }

        function Wa(d, f, g, h, j, k) {
            d = d | 0;
            f = f | 0;
            g = g | 0;
            h = h | 0;
            j = j | 0;
            k = k | 0;
            var l = 0, m = 0, n = 0, o = 0, p = 0, q = 0, r = 0, s = 0, t = 0, u = 0, v = 0, w = 0, x = 0, y = 0, z = 0,
                A = 0, B = 0, C = 0, D = 0, E = 0, F = 0, G = 0, H = 0, I = 0, J = 0, K = 0, L = 0, M = 0, N = 0, O = 0,
                P = 0, Q = 0, R = 0, S = 0, T = 0, U = 0, V = 0, W = 0, X = 0, Y = 0, _ = 0, $ = 0, aa = 0, ba = 0,
                ca = 0, da = 0, ea = 0, fa = 0, ga = 0, ha = 0, ia = 0, ja = 0, ka = 0, la = 0, ma = 0, na = 0, oa = 0,
                pa = 0, qa = 0, ra = 0, sa = 0, ta = 0, ua = 0, va = 0, wa = 0, xa = 0, ya = 0, za = 0, Aa = 0, Ba = 0,
                Ca = 0, Ea = 0, Fa = 0, Ga = 0, Ha = 0, Ja = 0, La = 0, Ta = 0, Ua = 0, Wa = 0, bb = 0, db = 0, eb = 0,
                ib = 0, mb = 0, pb = 0, rb = 0, tb = 0, xb = 0, yb = 0, zb = 0, Ab = 0, Bb = 0;
            Bb = i;
            i = i + 336 | 0;
            r = Bb + 236 | 0;
            q = Bb + 216 | 0;
            zb = Bb + 112 | 0;
            yb = Bb + 12 | 0;
            mb = Bb + 256 | 0;
            rb = Bb + 136 | 0;
            pb = Bb + 32 | 0;
            eb = Bb + 8 | 0;
            ib = Bb + 6 | 0;
            xb = Bb + 4 | 0;
            tb = Bb + 2 | 0;
            Ab = Bb;
            Ta = d + 1164 | 0;
            Ua = d + 748 | 0;
            Wa = hb(Ua, h, Ta) | 0;
            if (Wa) {
                _abort();//fix cc 精简
            }
            switch (h | 0) {
                case 1: {
                    l = 1;
                    x = 6;
                    break
                }
                case 2:
                case 7: {
                    _abort();//fix cc 精简
                    break
                }
                case 3: {
                    x = 9;
                    break
                }
                default: {
                    l = 0;
                    x = 6
                }
            }
            do if ((x | 0) == 6) {
                h = d + 440 | 0;
                if ((b[h >> 1] | 0) == 6) {
                    _abort();//fix cc 精简
                } else {
                    b[h >> 1] = 0;
                    Ja = 0;
                    La = 0;
                    break
                }
            } else if ((x | 0) == 9) {
                _abort();//fix cc 精简
            } while (0);
            Ea = d + 1156 | 0;
            switch (c[Ea >> 2] | 0) {
                case 1: {
                    b[h >> 1] = 5;
                    b[d + 436 >> 1] = 0;
                    break
                }
                case 2: {
                    b[h >> 1] = 5;
                    b[d + 436 >> 1] = 1;
                    break
                }
                default: {
                }
            }
            n = d + 646 | 0;
            Fa = d + 666 | 0;
            m = zb;
            o = Fa;
            p = m + 20 | 0;
            do {
                a[m >> 0] = a[o >> 0] | 0;
                m = m + 1 | 0;
                o = o + 1 | 0
            } while ((m | 0) < (p | 0));
            Ga = (f | 0) != 7;
            Ha = d + 1168 | 0;
            if (Ga) {
                ab(n, f, La, g, Ha, r, Ta);
                m = d + 392 | 0;
                ae(m, r, k, Ta);
                g = g + 6 | 0
            } else {
                cb(n, La, g, Ha, q, r, Ta);
                m = d + 392 | 0;
                _d(m, q, r, k, Ta);
                g = g + 10 | 0
            }
            o = r;
            p = m + 20 | 0;
            do {
                b[m >> 1] = b[o >> 1] | 0;
                m = m + 2 | 0;
                o = o + 2 | 0
            } while ((m | 0) < (p | 0));
            Ca = f >>> 0 > 1;
            B = f >>> 0 < 4 & 1;
            Ba = (f | 0) == 5;
            Aa = Ba ? 10 : 5;
            Ba = Ba ? 19 : 9;
            E = d + 434 | 0;
            F = 143 - Ba & 65535;
            G = d + 460 | 0;
            H = d + 462 | 0;
            I = d + 464 | 0;
            C = f >>> 0 > 2;
            J = d + 388 | 0;
            K = (f | 0) == 0;
            L = f >>> 0 < 2;
            M = d + 1244 | 0;
            N = d + 432 | 0;
            O = f >>> 0 < 6;
            P = d + 1168 | 0;
            Q = (f | 0) == 6;
            R = La << 16 >> 16 == 0;
            S = d + 714 | 0;
            T = d + 686 | 0;
            U = d + 436 | 0;
            V = d + 700 | 0;
            W = (f | 0) == 7;
            X = d + 482 | 0;
            Y = f >>> 0 < 3;
            _ = d + 608 | 0;
            $ = d + 626 | 0;
            aa = d + 438 | 0;
            ba = f >>> 0 < 7;
            ca = d + 730 | 0;
            D = Ja ^ 1;
            da = l << 16 >> 16 != 0;
            za = da ? La ^ 1 : 0;
            ea = d + 442 | 0;
            fa = d + 458 | 0;
            ga = d + 412 | 0;
            ha = d + 80 | 0;
            ia = d + 1236 | 0;
            ja = d + 1240 | 0;
            ka = d + 468 | 0;
            la = d + 466 | 0;
            ma = d + 470 | 0;
            na = d + 472 | 0;
            oa = d + 474 | 0;
            pa = d + 476 | 0;
            qa = d + 478 | 0;
            ra = d + 480 | 0;
            sa = d + 444 | 0;
            ta = d + 446 | 0;
            ua = d + 448 | 0;
            va = d + 450 | 0;
            wa = d + 452 | 0;
            xa = d + 454 | 0;
            ya = d + 456 | 0;
            y = 0;
            z = 0;
            s = 0;
            t = 0;
            A = -1;
            while (1) {
                A = (A << 16 >> 16) + 1 | 0;
                p = A & 65535;
                z = 1 - (z << 16 >> 16) | 0;
                v = z & 65535;
                q = Ca & s << 16 >> 16 == 80 ? 0 : s;
                u = g + 2 | 0;
                r = b[g >> 1] | 0;
                a:do if (Ga) {
                    w = b[E >> 1] | 0;
                    m = (w & 65535) - Aa & 65535;
                    m = m << 16 >> 16 < 20 ? 20 : m;
                    o = (m & 65535) + Ba & 65535;
                    n = o << 16 >> 16 > 143;
                    Ya(r, n ? F : m, n ? 143 : o, q, w, eb, ib, B, Ta);
                    q = b[eb >> 1] | 0;
                    b[G >> 1] = q;
                    if (Ja) {
                        _abort();//fix cc 精简
                    } else {
                        r = q;
                        q = b[ib >> 1] | 0
                    }
                    se(c[J >> 2] | 0, r, q, 40, 1, Ta);
                    if (L) {
                        q = g + 6 | 0;
                        Pa(p, b[g + 4 >> 1] | 0, b[u >> 1] | 0, c[M >> 2] | 0, mb, Ta);
                        g = b[N >> 1] | 0;
                        w = g << 16 >> 16;
                        r = w << 1;
                        if ((r | 0) == (w << 17 >> 16 | 0)) {
                            o = K;
                            break
                        }
                        o = K;
                        r = g << 16 >> 16 > 0 ? 32767 : -32768;
                        break
                    }
                    switch (f | 0) {
                        case 2: {
                            q = g + 6 | 0;
                            Oa(b[g + 4 >> 1] | 0, b[u >> 1] | 0, mb);
                            g = b[N >> 1] | 0;
                            w = g << 16 >> 16;
                            r = w << 1;
                            if ((r | 0) == (w << 17 >> 16 | 0)) {
                                o = K;
                                break a
                            }
                            o = K;
                            r = g << 16 >> 16 > 0 ? 32767 : -32768;
                            break a
                        }
                        case 3: {
                            q = g + 6 | 0;
                            Qa(b[g + 4 >> 1] | 0, b[u >> 1] | 0, mb);
                            g = b[N >> 1] | 0;
                            w = g << 16 >> 16;
                            r = w << 1;
                            if ((r | 0) == (w << 17 >> 16 | 0)) {
                                o = K;
                                break a
                            }
                            o = K;
                            r = g << 16 >> 16 > 0 ? 32767 : -32768;
                            break a
                        }
                        default: {
                            if (O) {
                                q = g + 6 | 0;
                                Ra(b[g + 4 >> 1] | 0, b[u >> 1] | 0, c[P >> 2] | 0, mb);
                                g = b[N >> 1] | 0;
                                w = g << 16 >> 16;
                                r = w << 1;
                                if ((r | 0) == (w << 17 >> 16 | 0)) {
                                    o = K;
                                    break a
                                }
                                o = K;
                                r = g << 16 >> 16 > 0 ? 32767 : -32768;
                                break a
                            }
                            if (!Q) {
                                o = K;
                                x = 44;
                                break a
                            }
                            Sa(u, mb, Ta);
                            r = g + 16 | 0;
                            g = b[N >> 1] | 0;
                            w = g << 16 >> 16;
                            p = w << 1;
                            if ((p | 0) == (w << 17 >> 16 | 0)) {
                                q = r;
                                o = K;
                                r = p;
                                break a
                            }
                            q = r;
                            o = K;
                            r = g << 16 >> 16 > 0 ? 32767 : -32768;
                            break a
                        }
                    }
                } else {
                    Za(r, 18, 143, q, eb, ib, Ta);
                    if (R ? q << 16 >> 16 == 0 | r << 16 >> 16 < 61 : 0) {
                        r = b[eb >> 1] | 0;
                        q = b[ib >> 1] | 0
                    } else { //不可精简
                        b[G >> 1] = b[eb >> 1] | 0;
                        r = b[E >> 1] | 0;
                        b[eb >> 1] = r;
                        b[ib >> 1] = 0;
                        q = 0
                    }
                    se(c[J >> 2] | 0, r, q, 40, 0, Ta);
                    o = 0;
                    x = 44
                } while (0);
                if ((x | 0) == 44) {
                    x = 0;
                    if (Ja) lb(T, b[h >> 1] | 0, xb, Ta); else b[xb >> 1] = $a(f, b[u >> 1] | 0, c[ja >> 2] | 0) | 0;
                    nb(T, La, b[U >> 1] | 0, xb, Ta);
                    Na(g + 4 | 0, mb, c[P >> 2] | 0);
                    r = g + 24 | 0;
                    g = b[xb >> 1] | 0;
                    w = g << 16 >> 16;
                    p = w << 1;
                    if ((p | 0) == (w << 17 >> 16 | 0)) {
                        q = r;
                        r = p
                    } else {
                        q = r;
                        r = g << 16 >> 16 > 0 ? 32767 : -32768
                    }
                }
                g = b[eb >> 1] | 0;
                b:do if (g << 16 >> 16 < 40) {
                    m = r << 16 >> 16;
                    n = g;
                    r = g << 16 >> 16;
                    while (1) {
                        p = mb + (r << 1) | 0;
                        g = (Z(b[mb + (r - (n << 16 >> 16) << 1) >> 1] | 0, m) | 0) >> 15;
                        if ((g | 0) > 32767) {
                            c[Ta >> 2] = 1;
                            g = 32767
                        }
                        w = g & 65535;
                        b[Ab >> 1] = w;
                        b[p >> 1] = Rd(b[p >> 1] | 0, w, Ta) | 0;
                        r = r + 1 | 0;
                        if ((r & 65535) << 16 >> 16 == 40) break b;
                        n = b[eb >> 1] | 0
                    }
                } while (0);
                c:do if (o) {
                    o = (z & 65535 | 0) == 0;
                    if (o) {
                        g = q;
                        p = t
                    } else {
                        g = q + 2 | 0;
                        p = b[q >> 1] | 0
                    }
                    if (R) Xa(S, f, p, mb, v, xb, tb, Ha, Ta); else {
                        _abort();//fix cc 精简
                    }
                    nb(T, La, b[U >> 1] | 0, xb, Ta);
                    kb(V, La, b[U >> 1] | 0, tb, Ta);
                    q = b[xb >> 1] | 0;
                    r = q << 16 >> 16 > 13017 ? 13017 : q;
                    if (o) x = 80; else w = p
                } else {
                    g = q + 2 | 0;
                    r = b[q >> 1] | 0;
                    switch (f | 0) {
                        case 1:
                        case 2:
                        case 3:
                        case 4:
                        case 6: {
                            if (R) Xa(S, f, r, mb, v, xb, tb, Ha, Ta); else {
                                _abort();//fix cc 精简
                            }
                            nb(T, La, b[U >> 1] | 0, xb, Ta);
                            kb(V, La, b[U >> 1] | 0, tb, Ta);
                            q = b[xb >> 1] | 0;
                            r = q << 16 >> 16 > 13017 ? 13017 : q;
                            if (!Q) {
                                p = t;
                                x = 80;
                                break c
                            }
                            if ((b[E >> 1] | 0) <= 45) {
                                p = t;
                                x = 80;
                                break c
                            }
                            p = t;
                            r = r << 16 >> 16 >>> 2 & 65535;
                            x = 80;
                            break c
                        }
                        case 5: {
                            if (Ja) lb(T, b[h >> 1] | 0, xb, Ta); else b[xb >> 1] = $a(5, r, c[ja >> 2] | 0) | 0;
                            nb(T, La, b[U >> 1] | 0, xb, Ta);
                            if (R) _a(S, 5, b[g >> 1] | 0, mb, c[ia >> 2] | 0, tb, Ta); else jb(V, S, b[h >> 1] | 0, tb, Ta);
                            kb(V, La, b[U >> 1] | 0, tb, Ta);
                            r = b[xb >> 1] | 0;
                            g = q + 4 | 0;
                            q = r;
                            p = t;
                            r = r << 16 >> 16 > 13017 ? 13017 : r;
                            x = 80;
                            break c
                        }
                        default: {
                            if (R) _a(S, f, r, mb, c[ia >> 2] | 0, tb, Ta); else jb(V, S, b[h >> 1] | 0, tb, Ta);
                            kb(V, La, b[U >> 1] | 0, tb, Ta);
                            r = b[xb >> 1] | 0;
                            q = r;
                            p = t;
                            x = 80;
                            break c
                        }
                    }
                } while (0);
                if ((x | 0) == 80) {
                    x = 0;
                    b[N >> 1] = q << 16 >> 16 > 13017 ? 13017 : q;
                    w = p
                }
                r = r << 16 >> 16;
                r = (r << 17 >> 17 | 0) == (r | 0) ? r << 1 : r >>> 15 ^ 32767;
                v = (r & 65535) << 16 >> 16 > 16384;
                d:do if (v) {
                    u = r << 16 >> 16;
                    if (W) q = 0; else {
                        q = 0;
                        while (1) {
                            r = (Z(b[(c[J >> 2] | 0) + (q << 1) >> 1] | 0, u) | 0) >> 15;
                            if ((r | 0) > 32767) {
                                c[Ta >> 2] = 1;
                                r = 32767
                            }
                            b[Ab >> 1] = r;
                            r = Z(b[xb >> 1] | 0, r << 16 >> 16) | 0;
                            if ((r | 0) == 1073741824) {
                                _abort();//fix cc 精简
                            } else r = r << 1;
                            b[rb + (q << 1) >> 1] = Ce(r, Ta) | 0;
                            q = q + 1 | 0;
                            if ((q | 0) == 40) break d
                        }
                    }
                    do {
                        r = (Z(b[(c[J >> 2] | 0) + (q << 1) >> 1] | 0, u) | 0) >> 15;
                        if ((r | 0) > 32767) {
                            c[Ta >> 2] = 1;
                            r = 32767
                        }
                        b[Ab >> 1] = r;
                        r = Z(b[xb >> 1] | 0, r << 16 >> 16) | 0;
                        if ((r | 0) != 1073741824) {
                            r = r << 1;
                            if ((r | 0) < 0) r = ~((r ^ -2) >> 1); else x = 88
                        } else {
                            _abort();//fix cc 精简
                        }
                        if ((x | 0) == 88) {
                            x = 0;
                            r = r >> 1
                        }
                        b[rb + (q << 1) >> 1] = Ce(r, Ta) | 0;
                        q = q + 1 | 0
                    } while ((q | 0) != 40)
                } while (0);
                if (R) {
                    b[la >> 1] = b[ka >> 1] | 0;
                    b[ka >> 1] = b[ma >> 1] | 0;
                    b[ma >> 1] = b[na >> 1] | 0;
                    b[na >> 1] = b[oa >> 1] | 0;
                    b[oa >> 1] = b[pa >> 1] | 0;
                    b[pa >> 1] = b[qa >> 1] | 0;
                    b[qa >> 1] = b[ra >> 1] | 0;
                    b[ra >> 1] = b[X >> 1] | 0;
                    b[X >> 1] = b[xb >> 1] | 0
                }
                if ((Ja | (b[U >> 1] | 0) != 0 ? Y & (b[H >> 1] | 0) != 0 : 0) ? (bb = b[xb >> 1] | 0, bb << 16 >> 16 > 12288) : 0) {
                    _abort();//fix cc 精简
                }
                qb(zb, Fa, s, yb, Ta);
                r = Ma(_, f, b[tb >> 1] | 0, yb, $, La, b[U >> 1] | 0, l, b[aa >> 1] | 0, b[H >> 1] | 0, b[I >> 1] | 0, Ta) | 0;
                switch (f | 0) {
                    case 0:
                    case 1:
                    case 2:
                    case 3:
                    case 6: {
                        p = b[xb >> 1] | 0;
                        u = 1;
                        break
                    }
                    default: {
                        r = b[tb >> 1] | 0;
                        p = b[xb >> 1] | 0;
                        if (ba) u = 1; else {
                            q = p << 16 >> 16;
                            if (p << 16 >> 16 < 0) q = ~((q ^ -2) >> 1); else q = q >>> 1;
                            p = q & 65535;
                            u = 2
                        }
                    }
                }
                m = p << 16 >> 16;
                s = u & 65535;
                q = c[J >> 2] | 0;
                t = 0;
                do {
                    q = q + (t << 1) | 0;
                    b[pb + (t << 1) >> 1] = b[q >> 1] | 0;
                    q = Z(b[q >> 1] | 0, m) | 0;
                    if ((q | 0) == 1073741824) {
                        c[Ta >> 2] = 1;
                        n = 2147483647
                    } else n = q << 1;
                    o = Z(b[tb >> 1] | 0, b[mb + (t << 1) >> 1] | 0) | 0;
                    if ((o | 0) != 1073741824) {
                        q = (o << 1) + n | 0;
                        if ((o ^ n | 0) > 0 & (q ^ n | 0) < 0) {
                            _abort();//fix cc 精简
                        }
                    } else {
                        c[Ta >> 2] = 1;
                        q = 2147483647
                    }
                    x = q << s;
                    x = Ce((x >> s | 0) == (q | 0) ? x : q >> 31 ^ 2147483647, Ta) | 0;
                    q = c[J >> 2] | 0;
                    b[q + (t << 1) >> 1] = x;
                    t = t + 1 | 0
                } while ((t | 0) != 40);
                vb(ca);
                if ((Y ? (b[I >> 1] | 0) > 3 : 0) ? !((b[H >> 1] | 0) == 0 | D) : 0) ub(ca);
                wb(ca, f, pb, r, b[xb >> 1] | 0, mb, p, u, Ha, Ta);
                r = 0;
                o = 0;
                do {
                    q = b[pb + (o << 1) >> 1] | 0;
                    q = Z(q, q) | 0;
                    if ((q | 0) != 1073741824) {
                        p = (q << 1) + r | 0;
                        if ((q ^ r | 0) > 0 & (p ^ r | 0) < 0) {//不可精简
                            c[Ta >> 2] = 1;
                            r = (r >>> 31) + 2147483647 | 0
                        } else r = p
                    } else {
                        c[Ta >> 2] = 1;
                        r = 2147483647
                    }
                    o = o + 1 | 0
                } while ((o | 0) != 40);
                if ((r | 0) < 0) r = ~((r ^ -2) >> 1); else r = r >> 1;
                r = Fe(r, Ab, Ta) | 0;
                p = ((b[Ab >> 1] | 0) >>> 1) + 15 | 0;
                q = p & 65535;
                p = p << 16 >> 16;
                if (q << 16 >> 16 > 0) if (q << 16 >> 16 < 31) {
                    r = r >> p;
                    x = 135
                } else {
                    r = 0;
                    x = 137
                } else {
                    _abort();//fix cc 精简
                }
                if ((x | 0) == 135) {
                    x = 0;
                    if ((r | 0) < 0) r = ~((r ^ -4) >> 2); else x = 137
                }
                if ((x | 0) == 137) {
                    x = 0;
                    r = r >>> 2
                }
                r = r & 65535;
                do if (Y ? (db = b[I >> 1] | 0, db << 16 >> 16 > 5) : 0) if (b[H >> 1] | 0) if ((b[h >> 1] | 0) < 4) {//不可精简
                    if (da) {
                        if (!(Ja | (b[aa >> 1] | 0) != 0)) x = 145
                    } else if (!Ja) x = 145;
                    if ((x | 0) == 145 ? (0, (b[U >> 1] | 0) == 0) : 0) {
                        x = 147;
                        break
                    }
                    _abort();//fix cc 精简
					
                } else x = 147; else x = 151; else x = 147; while (0);
                do if ((x | 0) == 147) {
                    x = 0;
                    if (b[H >> 1] | 0) {
                        if (!Ja ? (b[U >> 1] | 0) == 0 : 0) {
                            x = 151;
                            break
                        }
                        if ((b[h >> 1] | 0) >= 4) x = 151
                    } else x = 151
                } while (0);
                if ((x | 0) == 151) {
                    x = 0;
                    b[ea >> 1] = b[sa >> 1] | 0;
                    b[sa >> 1] = b[ta >> 1] | 0;
                    b[ta >> 1] = b[ua >> 1] | 0;
                    b[ua >> 1] = b[va >> 1] | 0;
                    b[va >> 1] = b[wa >> 1] | 0;
                    b[wa >> 1] = b[xa >> 1] | 0;
                    b[xa >> 1] = b[ya >> 1] | 0;
                    b[ya >> 1] = b[fa >> 1] | 0;
                    b[fa >> 1] = r
                }
                if (v) {
                    r = 0;
                    do {
                        v = rb + (r << 1) | 0;
                        b[v >> 1] = Rd(b[v >> 1] | 0, b[pb + (r << 1) >> 1] | 0, Ta) | 0;
                        r = r + 1 | 0
                    } while ((r | 0) != 40);
                    Da(pb, rb, 40, Ta);
                    c[Ta >> 2] = 0;
                    He(k, rb, j + (y << 1) | 0, 40, ga, 0)
                } else {
                    c[Ta >> 2] = 0;
                    He(k, pb, j + (y << 1) | 0, 40, ga, 0)
                }
                if (!(c[Ta >> 2] | 0)) Pe(ga | 0, j + (y + 30 << 1) | 0, 20) | 0; else {
                    _abort();//fix cc 精简
                }
                Pe(d | 0, ha | 0, 308) | 0;
                b[E >> 1] = b[eb >> 1] | 0;
                r = y + 40 | 0;
                s = r & 65535;
                if (s << 16 >> 16 >= 160) break; else {
                    y = r << 16 >> 16;
                    k = k + 22 | 0;
                    t = w
                }
            }
            b[H >> 1] = Ka(d + 484 | 0, d + 466 | 0, j, I, Ta) | 0;
            gb(Ua, Fa, j, Ta);
            b[U >> 1] = La;
            b[aa >> 1] = l;
            sb(d + 626 | 0, Fa, Ta);
            Ab = Ea;
            c[Ab >> 2] = Wa;
            i = Bb;
            return
        }

        function Xa(a, d, f, g, h, j, k, l, m) {
            a = a | 0;
            d = d | 0;
            f = f | 0;
            g = g | 0;
            h = h | 0;
            j = j | 0;
            k = k | 0;
            l = l | 0;
            m = m | 0;
            var n = 0, o = 0, p = 0, q = 0, r = 0;
            r = i;
            i = i + 16 | 0;
            p = r + 2 | 0;
            q = r;
            f = f << 16 >> 16;
            f = (f << 18 >> 18 | 0) == (f | 0) ? f << 2 : f >>> 15 ^ 32767;
            switch (d | 0) {
                case 3:
                case 4:
                case 6: {
                    o = f << 16 >> 16;
                    f = c[l + 84 >> 2] | 0;
                    b[j >> 1] = b[f + (o << 1) >> 1] | 0;
                    l = b[f + (o + 1 << 1) >> 1] | 0;
                    n = b[f + (o + 3 << 1) >> 1] | 0;
                    j = b[f + (o + 2 << 1) >> 1] | 0;
                    break
                }
                case 0: {
                    l = (f & 65535) + (h << 16 >> 16 << 1 ^ 2) | 0;
                    l = (l & 65535) << 16 >> 16 > 1022 ? 1022 : l << 16 >> 16;
                    b[j >> 1] = b[782 + (l << 1) >> 1] | 0;
                    j = b[782 + (l + 1 << 1) >> 1] | 0;
                    de(j << 16 >> 16, q, p, m);
                    b[q >> 1] = (e[q >> 1] | 0) + 65524;
                    l = Ee(b[p >> 1] | 0, 5, m) | 0;
                    o = b[q >> 1] | 0;
                    o = Rd(l, ((o << 26 >> 26 | 0) == (o | 0) ? o << 10 : o >>> 15 ^ 32767) & 65535, m) | 0;
                    l = b[p >> 1] | 0;
                    f = b[q >> 1] | 0;
                    if ((f * 24660 | 0) == 1073741824) {
                        c[m >> 2] = 1;
                        h = 2147483647
                    } else h = f * 49320 | 0;
                    n = (l << 16 >> 16) * 24660 >> 15;
                    f = h + (n << 1) | 0;
                    if ((h ^ n | 0) > 0 & (f ^ h | 0) < 0) {
                        c[m >> 2] = 1;
                        f = (h >>> 31) + 2147483647 | 0
                    }
                    n = f << 13;
                    l = j;
                    n = Ce((n >> 13 | 0) == (f | 0) ? n : f >> 31 ^ 2147483647, m) | 0;
                    j = o;
                    break
                }
                default: {
                    o = f << 16 >> 16;
                    f = c[l + 80 >> 2] | 0;
                    b[j >> 1] = b[f + (o << 1) >> 1] | 0;
                    l = b[f + (o + 1 << 1) >> 1] | 0;
                    n = b[f + (o + 3 << 1) >> 1] | 0;
                    j = b[f + (o + 2 << 1) >> 1] | 0
                }
            }
            Vd(a, d, g, q, p, 0, 0, m);
            h = Z((re(14, b[p >> 1] | 0, m) | 0) << 16 >> 16, l << 16 >> 16) | 0;
            if ((h | 0) == 1073741824) {
                c[m >> 2] = 1;
                f = 2147483647
            } else f = h << 1;
            l = 10 - (e[q >> 1] | 0) | 0;
            h = l & 65535;
            l = l << 16 >> 16;
            if (h << 16 >> 16 > 0) {
                q = h << 16 >> 16 < 31 ? f >> l : 0;
                q = q >>> 16;
                q = q & 65535;
                b[k >> 1] = q;
                Wd(a, j, n);
                i = r;
                return
            } else {//不可精简
                m = 0 - l << 16 >> 16;
                q = f << m;
                q = (q >> m | 0) == (f | 0) ? q : f >> 31 ^ 2147483647;
                q = q >>> 16;
                q = q & 65535;
                b[k >> 1] = q;
                Wd(a, j, n);
                i = r;
                return
            }
        }

        function Ya(a, d, e, f, g, h, i, j, k) {
            a = a | 0;
            d = d | 0;
            e = e | 0;
            f = f | 0;
            g = g | 0;
            h = h | 0;
            i = i | 0;
            j = j | 0;
            k = k | 0;
            if (!(f << 16 >> 16)) {
                j = a << 16 >> 16;
                if (a << 16 >> 16 >= 197) {
                    b[h >> 1] = j + 65424;
                    b[i >> 1] = 0;
                    return
                }
                g = ((j << 16) + 131072 >> 16) * 10923 >> 15;
                if ((g | 0) > 32767) {
                    c[k >> 2] = 1;
                    g = 32767
                }
                a = (g & 65535) + 19 | 0;
                b[h >> 1] = a;
                b[i >> 1] = j + 58 - ((a * 196608 | 0) >>> 16);
                return
            }
            if (!(j << 16 >> 16)) {
                k = a << 16 >> 16 << 16;
                a = ((k + 131072 >> 16) * 21846 | 0) + -65536 >> 16;
                b[h >> 1] = a + (d & 65535);
                b[i >> 1] = ((k + -131072 | 0) >>> 16) - ((a * 196608 | 0) >>> 16);
                return
            }
            if ((Ge(g, d, k) | 0) << 16 >> 16 > 5) g = (d & 65535) + 5 & 65535;
            j = e << 16 >> 16;
            j = (j - (g & 65535) & 65535) << 16 >> 16 > 4 ? j + 65532 & 65535 : g;
            g = a << 16 >> 16;
            if (a << 16 >> 16 < 4) {
                b[h >> 1] = ((((j & 65535) << 16) + -327680 | 0) >>> 16) + g;
                b[i >> 1] = 0;
                return
            }
            g = g << 16;
            if (a << 16 >> 16 < 12) {
                k = (((g + -327680 >> 16) * 10923 | 0) >>> 15 << 16) + -65536 | 0;
                a = k >> 16;
                b[h >> 1] = (j & 65535) + a;
                b[i >> 1] = ((g + -589824 | 0) >>> 16) - (k >>> 15) - a;
                return
            } else {//不可精简
                b[h >> 1] = ((g + -786432 + ((j & 65535) << 16) | 0) >>> 16) + 1;
                b[i >> 1] = 0;
                return
            }
        }

        function Za(a, c, d, f, g, h, i) {
            a = a | 0;
            c = c | 0;
            d = d | 0;
            f = f | 0;
            g = g | 0;
            h = h | 0;
            i = i | 0;
            if (f << 16 >> 16) {
                i = (e[g >> 1] | 0) + 65531 | 0;
                i = (i << 16 >> 16 | 0) < (c << 16 >> 16 | 0) ? c : i & 65535;
                d = d << 16 >> 16;
                c = a << 16 >> 16 << 16;
                a = ((c + 327680 >> 16) * 10924 | 0) + -65536 >> 16;
                b[g >> 1] = (((((i & 65535) << 16) + 589824 >> 16 | 0) > (d | 0) ? d + 65527 & 65535 : i) & 65535) + a;
                b[h >> 1] = ((c + -196608 | 0) >>> 16) - ((a * 393216 | 0) >>> 16);
                return
            }
            f = a << 16 >> 16;
            if (a << 16 >> 16 < 463) {
                a = ((((f << 16) + 327680 >> 16) * 10924 | 0) >>> 16) + 17 | 0;
                b[g >> 1] = a;
                b[h >> 1] = f + 105 - ((a * 393216 | 0) >>> 16);
                return
            } else {
                b[g >> 1] = f + 65168;
                b[h >> 1] = 0;
                return
            }
        }

        function _a(a, d, e, f, g, h, j) {
            a = a | 0;
            d = d | 0;
            e = e | 0;
            f = f | 0;
            g = g | 0;
            h = h | 0;
            j = j | 0;
            var k = 0, l = 0, m = 0, n = 0;
            n = i;
            i = i + 16 | 0;
            l = n + 6 | 0;
            k = n + 4 | 0;
            Vd(a, d, f, l, k, n + 2 | 0, n, j);
            m = (e & 31) * 3 | 0;
            f = g + (m << 1) | 0;
            if (!((Ge(d & 65535, 7, j) | 0) << 16 >> 16)) {
                l = re(b[l >> 1] | 0, b[k >> 1] | 0, j) | 0;
                k = l << 16 >> 16;
                k = (Z(((l << 20 >> 20 | 0) == (k | 0) ? l << 4 : k >>> 15 ^ 32767) << 16 >> 16, b[f >> 1] | 0) | 0) >> 15;
                if ((k | 0) > 32767) {
                    c[j >> 2] = 1;
                    k = 32767
                }
                f = k << 16;
                e = f >> 16;
                if ((k << 17 >> 17 | 0) == (e | 0)) k = f >> 15; else k = e >>> 15 ^ 32767
            } else {
                e = re(14, b[k >> 1] | 0, j) | 0;
                e = Z(e << 16 >> 16, b[f >> 1] | 0) | 0;
                if ((e | 0) == 1073741824) {
                    c[j >> 2] = 1;
                    f = 2147483647
                } else f = e << 1;
                e = Ge(9, b[l >> 1] | 0, j) | 0;
                k = e << 16 >> 16;
                if (e << 16 >> 16 > 0) k = e << 16 >> 16 < 31 ? f >> k : 0; else {
                    j = 0 - k << 16 >> 16;
                    k = f << j;
                    k = (k >> j | 0) == (f | 0) ? k : f >> 31 ^ 2147483647
                }
                k = k >>> 16
            }
            b[h >> 1] = k;
            Wd(a, b[g + (m + 1 << 1) >> 1] | 0, b[g + (m + 2 << 1) >> 1] | 0);
            i = n;
            return
        }

        function $a(a, c, d) {
            a = a | 0;
            c = c | 0;
            d = d | 0;
            c = b[d + (c << 16 >> 16 << 1) >> 1] | 0;
            if ((a | 0) != 7) {
                a = c;
                return a | 0
            }
            a = c & 65532;
            return a | 0
        }

        function ab(d, e, f, g, h, j, k) {
            d = d | 0;
            e = e | 0;
            f = f | 0;
            g = g | 0;
            h = h | 0;
            j = j | 0;
            k = k | 0;
            var l = 0, m = 0, n = 0, o = 0, p = 0, q = 0, r = 0, s = 0, t = 0, u = 0, v = 0;
            v = i;
            i = i + 48 | 0;
            r = v + 20 | 0;
            u = v;
            t = c[h + 44 >> 2] | 0;
            s = c[h + 64 >> 2] | 0;
            l = c[h + 4 >> 2] | 0;
            q = c[h + 12 >> 2] | 0;
            n = c[h + 20 >> 2] | 0;
            m = c[h + 56 >> 2] | 0;
            if (!(f << 16 >> 16)) {
                o = e >>> 0 < 2;
                if (o) {
                    f = 765;
                    p = 508;
                    n = c[h + 52 >> 2] | 0
                } else {
                    h = (e | 0) == 5;
                    f = h ? 1533 : 765;
                    p = 2044;
                    l = h ? m : l
                }
                m = b[g >> 1] | 0;
                f = ((m * 196608 >> 16 | 0) > (f & 65535 | 0) ? f : m * 3 & 65535) << 16 >> 16;
                m = b[l + (f << 1) >> 1] | 0;
                b[r >> 1] = m;
                b[r + 2 >> 1] = b[l + (f + 1 << 1) >> 1] | 0;
                b[r + 4 >> 1] = b[l + (f + 2 << 1) >> 1] | 0;
                f = b[g + 2 >> 1] | 0;
                if (o) f = f << 16 >> 16 << 1 & 65535;
                o = (f << 16 >> 16) * 196608 | 0;
                o = (o | 0) > 100466688 ? 1533 : o >> 16;
                b[r + 6 >> 1] = b[q + (o << 1) >> 1] | 0;
                b[r + 8 >> 1] = b[q + (o + 1 << 1) >> 1] | 0;
                b[r + 10 >> 1] = b[q + (o + 2 << 1) >> 1] | 0;
                g = b[g + 4 >> 1] | 0;
                g = ((g << 18 >> 16 | 0) > (p & 65535 | 0) ? p : g << 2 & 65535) << 16 >> 16;
                b[r + 12 >> 1] = b[n + (g << 1) >> 1] | 0;
                b[r + 14 >> 1] = b[n + ((g | 1) << 1) >> 1] | 0;
                b[r + 16 >> 1] = b[n + ((g | 2) << 1) >> 1] | 0;
                b[r + 18 >> 1] = b[n + ((g | 3) << 1) >> 1] | 0;
                if ((e | 0) == 8) {
                    _abort();//fix cc 精简
                } else l = 0;
                do {
                    m = d + (l << 1) | 0;
                    f = (Z(b[s + (l << 1) >> 1] | 0, b[m >> 1] | 0) | 0) >> 15;
                    if ((f | 0) > 32767) {
                        c[k >> 2] = 1;
                        f = 32767
                    }
                    g = Rd(b[t + (l << 1) >> 1] | 0, f & 65535, k) | 0;
                    e = b[r + (l << 1) >> 1] | 0;
                    b[u + (l << 1) >> 1] = Rd(e, g, k) | 0;
                    b[m >> 1] = e;
                    l = l + 1 | 0
                } while ((l | 0) != 10);
                Ae(u, 205, 10, k);
                l = d + 20 | 0;
                m = u;
                f = l + 20 | 0;
                do {
                    a[l >> 0] = a[m >> 0] | 0;
                    l = l + 1 | 0;
                    m = m + 1 | 0
                } while ((l | 0) < (f | 0));
                me(u, j, 10, k);
                i = v;
                return
            } else {
                _abort();//fix cc 精简
				return
            }
        }

        //fix cc 精简

        function cb(d, e, f, g, h, j, k) {
            d = d | 0;
            e = e | 0;
            f = f | 0;
            g = g | 0;
            h = h | 0;
            j = j | 0;
            k = k | 0;
            var l = 0, m = 0, n = 0, o = 0, p = 0, q = 0, r = 0, s = 0, t = 0, u = 0, v = 0;
            v = i;
            i = i + 80 | 0;
            q = v + 60 | 0;
            r = v + 40 | 0;
            t = v + 20 | 0;
            u = v;
            s = c[g + 48 >> 2] | 0;
            n = c[g + 24 >> 2] | 0;
            o = c[g + 28 >> 2] | 0;
            p = c[g + 32 >> 2] | 0;
            if (e << 16 >> 16) {
                _abort();//fix cc 精简
            }
            e = c[g + 16 >> 2] | 0;
            g = c[g + 8 >> 2] | 0;
            m = b[f >> 1] | 0;
            m = ((m << 18 >> 18 | 0) == (m | 0) ? m << 2 : m >>> 15 ^ 32767) << 16 >> 16;
            b[q >> 1] = b[g + (m << 1) >> 1] | 0;
            b[q + 2 >> 1] = b[g + (m + 1 << 1) >> 1] | 0;
            b[r >> 1] = b[g + (m + 2 << 1) >> 1] | 0;
            b[r + 2 >> 1] = b[g + (m + 3 << 1) >> 1] | 0;
            m = b[f + 2 >> 1] | 0;
            m = ((m << 18 >> 18 | 0) == (m | 0) ? m << 2 : m >>> 15 ^ 32767) << 16 >> 16;
            b[q + 4 >> 1] = b[e + (m << 1) >> 1] | 0;
            b[q + 6 >> 1] = b[e + (m + 1 << 1) >> 1] | 0;
            b[r + 4 >> 1] = b[e + (m + 2 << 1) >> 1] | 0;
            b[r + 6 >> 1] = b[e + (m + 3 << 1) >> 1] | 0;
            m = b[f + 4 >> 1] | 0;
            g = m << 16 >> 16;
            if (m << 16 >> 16 < 0) e = ~((g ^ -2) >> 1); else e = g >>> 1;
            m = e << 16 >> 16;
            m = ((e << 18 >> 18 | 0) == (m | 0) ? e << 2 : m >>> 15 ^ 32767) << 16 >> 16;
            l = n + (m + 1 << 1) | 0;
            e = b[n + (m << 1) >> 1] | 0;
            if (!(g & 1)) {
                b[q + 8 >> 1] = e;
                b[q + 10 >> 1] = b[l >> 1] | 0;
                b[r + 8 >> 1] = b[n + (m + 2 << 1) >> 1] | 0;
                b[r + 10 >> 1] = b[n + (m + 3 << 1) >> 1] | 0
            } else {
                if (e << 16 >> 16 == -32768) e = 32767; else e = 0 - (e & 65535) & 65535;
                b[q + 8 >> 1] = e;
                e = b[l >> 1] | 0;
                if (e << 16 >> 16 == -32768) e = 32767; else e = 0 - (e & 65535) & 65535;
                b[q + 10 >> 1] = e;
                e = b[n + (m + 2 << 1) >> 1] | 0;
                if (e << 16 >> 16 == -32768) e = 32767; else e = 0 - (e & 65535) & 65535;
                b[r + 8 >> 1] = e;
                e = b[n + (m + 3 << 1) >> 1] | 0;
                if (e << 16 >> 16 == -32768) e = 32767; else e = 0 - (e & 65535) & 65535;
                b[r + 10 >> 1] = e
            }
            l = b[f + 6 >> 1] | 0;
            l = ((l << 18 >> 18 | 0) == (l | 0) ? l << 2 : l >>> 15 ^ 32767) << 16 >> 16;
            b[q + 12 >> 1] = b[o + (l << 1) >> 1] | 0;
            b[q + 14 >> 1] = b[o + (l + 1 << 1) >> 1] | 0;
            b[r + 12 >> 1] = b[o + (l + 2 << 1) >> 1] | 0;
            b[r + 14 >> 1] = b[o + (l + 3 << 1) >> 1] | 0;
            l = b[f + 8 >> 1] | 0;
            l = ((l << 18 >> 18 | 0) == (l | 0) ? l << 2 : l >>> 15 ^ 32767) << 16 >> 16;
            b[q + 16 >> 1] = b[p + (l << 1) >> 1] | 0;
            b[q + 18 >> 1] = b[p + (l + 1 << 1) >> 1] | 0;
            b[r + 16 >> 1] = b[p + (l + 2 << 1) >> 1] | 0;
            b[r + 18 >> 1] = b[p + (l + 3 << 1) >> 1] | 0;
            l = 0;
            do {
                g = d + (l << 1) | 0;
                e = (b[g >> 1] | 0) * 21299 >> 15;
                if ((e | 0) > 32767) {
                    c[k >> 2] = 1;
                    e = 32767
                }
                p = Rd(b[s + (l << 1) >> 1] | 0, e & 65535, k) | 0;
                b[t + (l << 1) >> 1] = Rd(b[q + (l << 1) >> 1] | 0, p, k) | 0;
                f = b[r + (l << 1) >> 1] | 0;
                b[u + (l << 1) >> 1] = Rd(f, p, k) | 0;
                b[g >> 1] = f;
                l = l + 1 | 0
            } while ((l | 0) != 10);
            Ae(t, 205, 10, k);
            Ae(u, 205, 10, k);
            l = d + 20 | 0;
            g = u;
            e = l + 20 | 0;
            do {
                a[l >> 0] = a[g >> 0] | 0;
                l = l + 1 | 0;
                g = g + 1 | 0
            } while ((l | 0) < (e | 0));
            me(t, h, 10, k);
            me(u, j, 10, k);
            i = v;
            return
        }

        function db(a, c) {
            a = a | 0;
            c = c | 0;
            var d = 0, e = 0;
            if (!a) {
                e = -1;
                return e | 0
            }
            d = a;
            e = d + 20 | 0;
            do {
                b[d >> 1] = 0;
                d = d + 2 | 0
            } while ((d | 0) < (e | 0));
            Pe(a + 20 | 0, c | 0, 20) | 0;
            e = 0;
            return e | 0
        }

        function eb(d) {
            d = d | 0;
            var e = 0, f = 0, g = 0, h = 0, i = 0;
            if (!d) {
                i = -1;
                return i | 0
            }
            b[d >> 1] = 0;
            b[d + 2 >> 1] = 8192;
            e = d + 4 | 0;
            b[e >> 1] = 3500;
            b[d + 6 >> 1] = 3500;
            c[d + 8 >> 2] = 1887529304;
            b[d + 12 >> 1] = 3e4;
            b[d + 14 >> 1] = 26e3;
            b[d + 16 >> 1] = 21e3;
            b[d + 18 >> 1] = 15e3;
            b[d + 20 >> 1] = 8e3;
            b[d + 22 >> 1] = 0;
            b[d + 24 >> 1] = -8e3;
            b[d + 26 >> 1] = -15e3;
            b[d + 28 >> 1] = -21e3;
            b[d + 30 >> 1] = -26e3;
            b[d + 32 >> 1] = 3e4;
            b[d + 34 >> 1] = 26e3;
            b[d + 36 >> 1] = 21e3;
            b[d + 38 >> 1] = 15e3;
            b[d + 40 >> 1] = 8e3;
            b[d + 42 >> 1] = 0;
            b[d + 44 >> 1] = -8e3;
            b[d + 46 >> 1] = -15e3;
            b[d + 48 >> 1] = -21e3;
            b[d + 50 >> 1] = -26e3;
            b[d + 212 >> 1] = 0;
            b[d + 374 >> 1] = 0;
            b[d + 392 >> 1] = 0;
            f = d + 52 | 0;
            b[f >> 1] = 1384;
            b[d + 54 >> 1] = 2077;
            b[d + 56 >> 1] = 3420;
            b[d + 58 >> 1] = 5108;
            b[d + 60 >> 1] = 6742;
            b[d + 62 >> 1] = 8122;
            b[d + 64 >> 1] = 9863;
            b[d + 66 >> 1] = 11092;
            b[d + 68 >> 1] = 12714;
            b[d + 70 >> 1] = 13701;
            g = d + 72 | 0;
            h = f;
            i = g + 20 | 0;
            do {
                a[g >> 0] = a[h >> 0] | 0;
                g = g + 1 | 0;
                h = h + 1 | 0
            } while ((g | 0) < (i | 0));
            g = d + 92 | 0;
            h = f;
            i = g + 20 | 0;
            do {
                a[g >> 0] = a[h >> 0] | 0;
                g = g + 1 | 0;
                h = h + 1 | 0
            } while ((g | 0) < (i | 0));
            g = d + 112 | 0;
            h = f;
            i = g + 20 | 0;
            do {
                a[g >> 0] = a[h >> 0] | 0;
                g = g + 1 | 0;
                h = h + 1 | 0
            } while ((g | 0) < (i | 0));
            g = d + 132 | 0;
            h = f;
            i = g + 20 | 0;
            do {
                a[g >> 0] = a[h >> 0] | 0;
                g = g + 1 | 0;
                h = h + 1 | 0
            } while ((g | 0) < (i | 0));
            g = d + 152 | 0;
            h = f;
            i = g + 20 | 0;
            do {
                a[g >> 0] = a[h >> 0] | 0;
                g = g + 1 | 0;
                h = h + 1 | 0
            } while ((g | 0) < (i | 0));
            g = d + 172 | 0;
            h = f;
            i = g + 20 | 0;
            do {
                a[g >> 0] = a[h >> 0] | 0;
                g = g + 1 | 0;
                h = h + 1 | 0
            } while ((g | 0) < (i | 0));
            g = d + 192 | 0;
            h = f;
            i = g + 20 | 0;
            do {
                a[g >> 0] = a[h >> 0] | 0;
                g = g + 1 | 0;
                h = h + 1 | 0
            } while ((g | 0) < (i | 0));
            Qe(d + 214 | 0, 0, 160) | 0;
            b[d + 376 >> 1] = 3500;
            b[d + 378 >> 1] = 3500;
            i = b[e >> 1] | 0;
            b[d + 380 >> 1] = i;
            b[d + 382 >> 1] = i;
            b[d + 384 >> 1] = i;
            b[d + 386 >> 1] = i;
            b[d + 388 >> 1] = i;
            b[d + 390 >> 1] = i;
            b[d + 394 >> 1] = 0;
            b[d + 396 >> 1] = 7;
            b[d + 398 >> 1] = 32767;
            b[d + 400 >> 1] = 0;
            b[d + 402 >> 1] = 0;
            b[d + 404 >> 1] = 0;
            c[d + 408 >> 2] = 1;
            b[d + 412 >> 1] = 0;
            i = 0;
            return i | 0
        }

        //fix cc 精简

        function gb(a, d, f, g) {
            a = a | 0;
            d = d | 0;
            f = f | 0;
            g = g | 0;
            var h = 0, j = 0, k = 0, l = 0, m = 0, n = 0;
            m = i;
            i = i + 16 | 0;
            k = m + 2 | 0;
            l = m;
            b[l >> 1] = 0;
            j = a + 212 | 0;
            h = (e[j >> 1] | 0) + 10 | 0;
            h = (h & 65535 | 0) == 80 ? 0 : h & 65535;
            b[j >> 1] = h;
            Pe(a + 52 + (h << 16 >> 16 << 1) | 0, d | 0, 20) | 0;
            h = 0;
            j = 159;
            while (1) {
                n = b[f + (j << 1) >> 1] | 0;
                n = Z(n, n) | 0;
                n = (n | 0) == 1073741824 ? 2147483647 : n << 1;
                d = n + h | 0;
                if ((n ^ h | 0) > -1 & (d ^ h | 0) < 0) {
                    c[g >> 2] = 1;
                    h = (h >>> 31) + 2147483647 | 0
                } else h = d;
                if ((j | 0) > 0) j = j + -1 | 0; else break
            }
            de(h, k, l, g);
            h = b[k >> 1] | 0;
            n = h << 16 >> 16;
            d = n << 10;
            if ((d | 0) != (n << 26 >> 16 | 0)) {
                c[g >> 2] = 1;
                d = h << 16 >> 16 > 0 ? 32767 : -32768
            }
            b[k >> 1] = d;
            n = b[l >> 1] | 0;
            h = n << 16 >> 16;
            if (n << 16 >> 16 < 0) h = ~((h ^ -32) >> 5); else h = h >>> 5;
            l = a + 392 | 0;
            n = (e[l >> 1] | 0) + 1 | 0;
            n = (n & 65535 | 0) == 8 ? 0 : n & 65535;
            b[l >> 1] = n;
            b[a + 376 + (n << 16 >> 16 << 1) >> 1] = h + 57015 + d;
            i = m;
            return
        }

        function hb(a, d, f) {
            a = a | 0;
            d = d | 0;
            f = f | 0;
            var g = 0, h = 0, i = 0, j = 0, k = 0, l = 0, m = 0, n = 0;
            l = (d | 0) == 4;
            m = (d | 0) == 5;
            n = (d | 0) == 6;
            g = c[a + 408 >> 2] | 0;
            a:do if ((d + -4 | 0) >>> 0 < 3) k = 4; else {
                if ((g + -1 | 0) >>> 0 < 2) switch (d | 0) {
                    case 2:
                    case 3:
                    case 7: {
                        k = 4;
                        break a
                    }
                    default: {
                    }
                }
                b[a >> 1] = 0;
                j = 0
            } while (0);
            if ((k | 0) == 4) {
                _abort();//fix cc 精简
            }
            i = a + 398 | 0;
            if (m & (b[a + 412 >> 1] | 0) == 0) {
                b[i >> 1] = 0;
                h = 0
            } else h = b[i >> 1] | 0;
            h = Rd(h, 1, f) | 0;
            b[i >> 1] = h;
            f = a + 404 | 0;
            b[f >> 1] = 0;
            c:do switch (d | 0) {
                case 2:
                case 4:
                case 5:
                case 6:
                case 7: {
                    if (!((d | 0) == 7 & (j | 0) == 0)) {
                        _abort();//fix cc 精简
                    } else k = 14;
                    break
                }
                default:
                    k = 14
            } while (0);
            if ((k | 0) == 14) b[a + 396 >> 1] = 7;
            if (!j) return j | 0;
            h = a + 400 | 0;
            b[h >> 1] = 0;
            g = a + 402 | 0;
            b[g >> 1] = 0;
            if (l) {
                b[h >> 1] = 1;
                return j | 0
            }
            if (m) {
                b[h >> 1] = 1;
                b[g >> 1] = 1;
                return j | 0
            }
            if (!n) return j | 0;
            b[h >> 1] = 1;
            b[f >> 1] = 0;
            return j | 0
        }

        function ib(a) {
            a = a | 0;
            if (!a) {
                a = -1;
                return a | 0
            }
            b[a >> 1] = 1;
            b[a + 2 >> 1] = 1;
            b[a + 4 >> 1] = 1;
            b[a + 6 >> 1] = 1;
            b[a + 8 >> 1] = 1;
            b[a + 10 >> 1] = 0;
            b[a + 12 >> 1] = 1;
            a = 0;
            return a | 0
        }

        function jb(a, d, e, f, g) {
            a = a | 0;
            d = d | 0;
            e = e | 0;
            f = f | 0;
            g = g | 0;
            _abort();//fix cc 精简
            return
        }

        function kb(a, c, d, e, f) {
            a = a | 0;
            c = c | 0;
            d = d | 0;
            e = e | 0;
            f = f | 0;
            if (!(c << 16 >> 16)) {
                if (d << 16 >> 16) {
                    _abort();//fix cc 精简
                } else c = a + 12 | 0;
                b[c >> 1] = b[e >> 1] | 0
            }
            b[a + 10 >> 1] = b[e >> 1] | 0;
            f = a + 2 | 0;
            b[a >> 1] = b[f >> 1] | 0;
            d = a + 4 | 0;
            b[f >> 1] = b[d >> 1] | 0;
            f = a + 6 | 0;
            b[d >> 1] = b[f >> 1] | 0;
            a = a + 8 | 0;
            b[f >> 1] = b[a >> 1] | 0;
            b[a >> 1] = b[e >> 1] | 0;
            return
        }

        function lb(a, d, e, f) {
            a = a | 0;
            d = d | 0;
            e = e | 0;
            f = f | 0;
            _abort();//fix cc 精简
            return
        }

        function mb(a) {
            a = a | 0;
            if (!a) {
                a = -1;
                return a | 0
            }
            b[a >> 1] = 1640;
            b[a + 2 >> 1] = 1640;
            b[a + 4 >> 1] = 1640;
            b[a + 6 >> 1] = 1640;
            b[a + 8 >> 1] = 1640;
            b[a + 10 >> 1] = 0;
            b[a + 12 >> 1] = 16384;
            a = 0;
            return a | 0
        }

        function nb(a, c, d, e, f) {
            a = a | 0;
            c = c | 0;
            d = d | 0;
            e = e | 0;
            f = f | 0;
            if (!(c << 16 >> 16)) {
                if (d << 16 >> 16) {
                    _abort();//fix cc 精简
                } else c = a + 12 | 0;
                b[c >> 1] = b[e >> 1] | 0
            }
            e = b[e >> 1] | 0;
            c = a + 10 | 0;
            b[c >> 1] = e;
            if ((Ge(e, 16384, f) | 0) << 16 >> 16 > 0) {
                b[c >> 1] = 16384;
                c = 16384
            } else c = b[c >> 1] | 0;
            f = a + 2 | 0;
            b[a >> 1] = b[f >> 1] | 0;
            e = a + 4 | 0;
            b[f >> 1] = b[e >> 1] | 0;
            f = a + 6 | 0;
            b[e >> 1] = b[f >> 1] | 0;
            a = a + 8 | 0;
            b[f >> 1] = b[a >> 1] | 0;
            b[a >> 1] = c;
            return
        }

        //fix cc 精简

        function qb(a, c, d, e, f) {
            a = a | 0;
            c = c | 0;
            d = d | 0;
            e = e | 0;
            f = f | 0;
            var g = 0, h = 0, i = 0, j = 0;
            switch (d << 16 >> 16) {
                case 0: {
                    j = 9;
                    while (1) {
                        i = b[a + (j << 1) >> 1] | 0;
                        d = i << 16 >> 16;
                        if (i << 16 >> 16 < 0) d = ~((d ^ -4) >> 2); else d = d >>> 2;
                        h = b[c + (j << 1) >> 1] | 0;
                        g = h << 16 >> 16;
                        if (h << 16 >> 16 < 0) h = ~((g ^ -4) >> 2); else h = g >>> 2;
                        b[e + (j << 1) >> 1] = Rd((i & 65535) - d & 65535, h & 65535, f) | 0;
                        if ((j | 0) > 0) j = j + -1 | 0; else break
                    }
                    return
                }
                case 40: {
                    h = 9;
                    while (1) {
                        f = b[a + (h << 1) >> 1] | 0;
                        d = f << 16 >> 16;
                        if (f << 16 >> 16 < 0) g = ~((d ^ -2) >> 1); else g = d >>> 1;
                        f = b[c + (h << 1) >> 1] | 0;
                        d = f << 16 >> 16;
                        if (f << 16 >> 16 < 0) d = ~((d ^ -2) >> 1); else d = d >>> 1;
                        b[e + (h << 1) >> 1] = d + g;
                        if ((h | 0) > 0) h = h + -1 | 0; else break
                    }
                    return
                }
                case 80: {
                    j = 9;
                    while (1) {
                        i = b[a + (j << 1) >> 1] | 0;
                        d = i << 16 >> 16;
                        if (i << 16 >> 16 < 0) i = ~((d ^ -4) >> 2); else i = d >>> 2;
                        d = b[c + (j << 1) >> 1] | 0;
                        g = d << 16 >> 16;
                        if (d << 16 >> 16 < 0) h = ~((g ^ -4) >> 2); else h = g >>> 2;
                        b[e + (j << 1) >> 1] = Rd(i & 65535, (d & 65535) - h & 65535, f) | 0;
                        if ((j | 0) > 0) j = j + -1 | 0; else break
                    }
                    return
                }
                case 120: {
                    b[e + 18 >> 1] = b[c + 18 >> 1] | 0;
                    b[e + 16 >> 1] = b[c + 16 >> 1] | 0;
                    b[e + 14 >> 1] = b[c + 14 >> 1] | 0;
                    b[e + 12 >> 1] = b[c + 12 >> 1] | 0;
                    b[e + 10 >> 1] = b[c + 10 >> 1] | 0;
                    b[e + 8 >> 1] = b[c + 8 >> 1] | 0;
                    b[e + 6 >> 1] = b[c + 6 >> 1] | 0;
                    b[e + 4 >> 1] = b[c + 4 >> 1] | 0;
                    b[e + 2 >> 1] = b[c + 2 >> 1] | 0;
                    b[e >> 1] = b[c >> 1] | 0;
                    return
                }
                default:
                    return
            }
        }

        function rb(a, b) {
            a = a | 0;
            b = b | 0;
            if (!a) {
                a = -1;
                return a | 0
            }
            Pe(a | 0, b | 0, 20) | 0;
            a = 0;
            return a | 0
        }

        function sb(a, d, e) {
            a = a | 0;
            d = d | 0;
            e = e | 0;
            var f = 0, g = 0, h = 0, i = 0, j = 0, k = 0, l = 0;
            l = 0;
            do {
                k = a + (l << 1) | 0;
                f = b[k >> 1] | 0;
                i = f & 65535;
                j = i << 16;
                f = f << 16 >> 16;
                if ((f * 5243 | 0) == 1073741824) {
                    c[e >> 2] = 1;
                    h = 2147483647
                } else h = f * 10486 | 0;
                g = j - h | 0;
                if (((g ^ j) & (h ^ j) | 0) < 0) {
                    c[e >> 2] = 1;
                    h = (i >>> 15) + 2147483647 | 0
                } else h = g;
                f = b[d + (l << 1) >> 1] | 0;
                g = f * 5243 | 0;
                if ((g | 0) != 1073741824) {
                    f = (f * 10486 | 0) + h | 0;
                    if ((g ^ h | 0) > 0 & (f ^ h | 0) < 0) {
                        c[e >> 2] = 1;
                        f = (h >>> 31) + 2147483647 | 0
                    }
                } else {
                    c[e >> 2] = 1;
                    f = 2147483647
                }
                b[k >> 1] = Ce(f, e) | 0;
                l = l + 1 | 0
            } while ((l | 0) != 10);
            return
        }

        function tb(a) {
            a = a | 0;
            var c = 0;
            if (!a) {
                c = -1;
                return c | 0
            }
            c = a + 18 | 0;
            do {
                b[a >> 1] = 0;
                a = a + 2 | 0
            } while ((a | 0) < (c | 0));
            c = 0;
            return c | 0
        }

        function ub(a) {
            a = a | 0;
            b[a + 14 >> 1] = 1;
            return
        }

        function vb(a) {
            a = a | 0;
            b[a + 14 >> 1] = 0;
            return
        }

        function wb(a, d, e, f, g, h, j, k, l, m) {
            a = a | 0;
            d = d | 0;
            e = e | 0;
            f = f | 0;
            g = g | 0;
            h = h | 0;
            j = j | 0;
            k = k | 0;
            l = l | 0;
            m = m | 0;
            var n = 0, o = 0, p = 0, q = 0, r = 0, s = 0, t = 0, u = 0, v = 0, w = 0, x = 0, y = 0, z = 0, A = 0, B = 0,
                C = 0;
            C = i;
            i = i + 160 | 0;
            z = C + 80 | 0;
            A = C;
            v = c[l + 120 >> 2] | 0;
            w = c[l + 124 >> 2] | 0;
            x = c[l + 128 >> 2] | 0;
            u = c[l + 132 >> 2] | 0;
            o = a + 6 | 0;
            t = a + 8 | 0;
            b[t >> 1] = b[o >> 1] | 0;
            r = a + 4 | 0;
            b[o >> 1] = b[r >> 1] | 0;
            s = a + 2 | 0;
            b[r >> 1] = b[s >> 1] | 0;
            b[s >> 1] = b[a >> 1] | 0;
            b[a >> 1] = g;
            l = g << 16 >> 16 < 14746 ? g << 16 >> 16 > 9830 & 1 : 2;
            n = a + 12 | 0;
            g = b[n >> 1] | 0;
            p = g << 15;
            do if ((p | 0) <= 536870911) if ((p | 0) < -536870912) {
                c[m >> 2] = 1;
                g = -2147483648;
                break
            } else {
                g = g << 17;
                break
            } else {
                c[m >> 2] = 1;
                g = 2147483647
            } while (0);
            y = f << 16 >> 16;
            q = a + 16 | 0;
            if ((Ce(g, m) | 0) << 16 >> 16 >= f << 16 >> 16) {
                p = b[q >> 1] | 0;
                if (p << 16 >> 16 > 0) {
                    p = (p & 65535) + 65535 & 65535;
                    b[q >> 1] = p
                }
                if (!(p << 16 >> 16)) {
                    g = (b[a >> 1] | 0) < 9830;
                    g = (b[s >> 1] | 0) < 9830 ? (g ? 2 : 1) : g & 1;
                    if ((b[r >> 1] | 0) < 9830) g = (g & 65535) + 1 & 65535;
                    if ((b[o >> 1] | 0) < 9830) g = (g & 65535) + 1 & 65535;
                    if ((b[t >> 1] | 0) < 9830) g = (g & 65535) + 1 & 65535;
                    p = 0;
                    l = g << 16 >> 16 > 2 ? 0 : l
                }
            } else {
                b[q >> 1] = 2;
                p = 2
            }
            s = l << 16 >> 16;
            t = a + 10 | 0;
            s = (p << 16 >> 16 == 0 ? (s | 0) > ((b[t >> 1] | 0) + 1 | 0) : 0) ? s + 65535 & 65535 : l;
            a = (b[a + 14 >> 1] | 0) == 1 ? 0 : f << 16 >> 16 < 10 ? 2 : s << 16 >> 16 < 2 & p << 16 >> 16 > 0 ? (s & 65535) + 1 & 65535 : s;
            b[t >> 1] = a;
            b[n >> 1] = f;
            switch (d | 0) {
                case 4:
                case 6:
                case 7:
                    break;
                default:
                    if (a << 16 >> 16 < 2) {
                        p = 0;
                        l = 0;
                        o = h;
                        n = z;
                        while (1) {
                            if (!(b[o >> 1] | 0)) g = 0; else {
                                l = l << 16 >> 16;
                                b[A + (l << 1) >> 1] = p;
                                g = b[o >> 1] | 0;
                                l = l + 1 & 65535
                            }
                            b[n >> 1] = g;
                            b[o >> 1] = 0;
                            p = p + 1 << 16 >> 16;
                            if (p << 16 >> 16 >= 40) {
                                t = l;
                                break
                            } else {
                                o = o + 2 | 0;
                                n = n + 2 | 0
                            }
                        }
                        s = a << 16 >> 16 == 0;
                        s = (d | 0) == 5 ? (s ? v : w) : s ? x : u;
                        if (t << 16 >> 16 > 0) {
                            r = 0;
                            do {
                                q = b[A + (r << 1) >> 1] | 0;
                                l = q << 16 >> 16;
                                a = b[z + (l << 1) >> 1] | 0;
                                if (q << 16 >> 16 < 40) {
                                    p = a << 16 >> 16;
                                    o = 39 - q & 65535;
                                    n = q;
                                    l = h + (l << 1) | 0;
                                    g = s;
                                    while (1) {
                                        d = (Z(b[g >> 1] | 0, p) | 0) >>> 15 & 65535;
                                        b[l >> 1] = Rd(b[l >> 1] | 0, d, m) | 0;
                                        n = n + 1 << 16 >> 16;
                                        if (n << 16 >> 16 >= 40) break; else {
                                            l = l + 2 | 0;
                                            g = g + 2 | 0
                                        }
                                    }
                                    if (q << 16 >> 16 > 0) {
                                        l = s + (o + 1 << 1) | 0;
                                        B = 36
                                    }
                                } else {
                                    l = s;
                                    B = 36
                                }
                                if ((B | 0) == 36) {
                                    B = 0;
                                    g = a << 16 >> 16;
                                    p = 0;
                                    o = h;
                                    while (1) {
                                        d = (Z(b[l >> 1] | 0, g) | 0) >>> 15 & 65535;
                                        b[o >> 1] = Rd(b[o >> 1] | 0, d, m) | 0;
                                        p = p + 1 << 16 >> 16;
                                        if (p << 16 >> 16 >= q << 16 >> 16) break; else {
                                            o = o + 2 | 0;
                                            l = l + 2 | 0
                                        }
                                    }
                                }
                                r = r + 1 | 0
                            } while ((r & 65535) << 16 >> 16 != t << 16 >> 16)
                        }
                    }
            }
            r = j << 16 >> 16;
            s = y << 1;
            g = k << 16 >> 16;
            n = 0 - g << 16;
            l = n >> 16;
            if (k << 16 >> 16 > 0) {
                p = 0;
                o = e;
                while (1) {
                    a = Z(b[e + (p << 1) >> 1] | 0, r) | 0;
                    if ((a | 0) == 1073741824) {
                        c[m >> 2] = 1;
                        n = 2147483647
                    } else n = a << 1;
                    k = Z(s, b[h >> 1] | 0) | 0;
                    a = k + n | 0;
                    if ((k ^ n | 0) > -1 & (a ^ n | 0) < 0) {
                        c[m >> 2] = 1;
                        a = (n >>> 31) + 2147483647 | 0
                    }
                    k = a << g;
                    b[o >> 1] = Ce((k >> g | 0) == (a | 0) ? k : a >> 31 ^ 2147483647, m) | 0;
                    p = p + 1 | 0;
                    if ((p | 0) == 40) break; else {
                        h = h + 2 | 0;
                        o = o + 2 | 0
                    }
                }
                i = C;
                return
            }
            _abort();//fix cc 精简
			return
        }

        function xb(a) {
            a = a | 0;
            if (!a) {
                a = -1;
                return a | 0
            }
            ;b[a >> 1] = 0;
            b[a + 2 >> 1] = 0;
            b[a + 4 >> 1] = 0;
            b[a + 6 >> 1] = 0;
            b[a + 8 >> 1] = 0;
            b[a + 10 >> 1] = 0;
            a = 0;
            return a | 0
        }

        function yb(a, c, d, e) {
            a = a | 0;
            c = c | 0;
            d = d | 0;
            e = e | 0;
            var f = 0, g = 0, h = 0, i = 0, j = 0, k = 0, l = 0, m = 0, n = 0, o = 0, p = 0, q = 0, r = 0;
            if (d << 16 >> 16 <= 0) return;
            f = a + 10 | 0;
            j = a + 8 | 0;
            l = a + 4 | 0;
            m = a + 6 | 0;
            n = a + 2 | 0;
            g = b[l >> 1] | 0;
            h = b[m >> 1] | 0;
            i = b[a >> 1] | 0;
            k = b[n >> 1] | 0;
            o = 0;
            while (1) {
                p = b[f >> 1] | 0;
                q = b[j >> 1] | 0;
                b[f >> 1] = q;
                r = b[c >> 1] | 0;
                b[j >> 1] = r;
                p = ((r << 16 >> 16) * 7699 | 0) + ((Z(i << 16 >> 16, -7667) | 0) + (((g << 16 >> 16) * 15836 | 0) + ((h << 16 >> 16) * 15836 >> 15)) + ((Z(k << 16 >> 16, -7667) | 0) >> 15)) + (Z(q << 16 >> 16, -15398) | 0) + ((p << 16 >> 16) * 7699 | 0) | 0;
                q = p << 3;
                p = (q >> 3 | 0) == (p | 0) ? q : p >> 31 ^ 2147483647;
                q = p << 1;
                b[c >> 1] = Ce((q >> 1 | 0) == (p | 0) ? q : p >> 31 ^ 2147483647, e) | 0;
                i = b[l >> 1] | 0;
                b[a >> 1] = i;
                k = b[m >> 1] | 0;
                b[n >> 1] = k;
                g = p >>> 16 & 65535;
                b[l >> 1] = g;
                h = (p >>> 1) - (p >> 16 << 15) & 65535;
                b[m >> 1] = h;
                o = o + 1 << 16 >> 16;
                if (o << 16 >> 16 >= d << 16 >> 16) break; else c = c + 2 | 0
            }
            return
        }

        function zb(a) {
            a = a | 0;
            if (!a) a = -1; else {
                b[a >> 1] = 0;
                a = 0
            }
            return a | 0
        }

        function Ab(a, d, e, f, g) {
            a = a | 0;
            d = d | 0;
            e = e | 0;
            f = f | 0;
            g = g | 0;
            var h = 0, i = 0, j = 0, k = 0;
            j = f << 16 >> 16;
            h = d + (j + -1 << 1) | 0;
            j = j + -2 | 0;
            k = b[h >> 1] | 0;
            if (f << 16 >> 16 < 2) f = e << 16 >> 16; else {
                f = e << 16 >> 16;
                i = 0;
                d = d + (j << 1) | 0;
                while (1) {
                    e = (Z(b[d >> 1] | 0, f) | 0) >> 15;
                    if ((e | 0) > 32767) {
                        c[g >> 2] = 1;
                        e = 32767
                    }
                    b[h >> 1] = Ge(b[h >> 1] | 0, e & 65535, g) | 0;
                    h = h + -2 | 0;
                    i = i + 1 << 16 >> 16;
                    if ((i << 16 >> 16 | 0) > (j | 0)) break; else d = d + -2 | 0
                }
            }
            f = (Z(b[a >> 1] | 0, f) | 0) >> 15;
            if ((f | 0) <= 32767) {
                j = f;
                j = j & 65535;
                i = b[h >> 1] | 0;
                g = Ge(i, j, g) | 0;
                b[h >> 1] = g;
                b[a >> 1] = k;
                return
            }
            c[g >> 2] = 1;
            j = 32767;
            j = j & 65535;
            i = b[h >> 1] | 0;
            g = Ge(i, j, g) | 0;
            b[h >> 1] = g;
            b[a >> 1] = k;
            return
        }

        function Bb(a) {
            a = a | 0;
            var c = 0, d = 0, e = 0;
            if (!a) {
                e = -1;
                return e | 0
            }
            Qe(a + 104 | 0, 0, 340) | 0;
            c = a + 102 | 0;
            d = a;
            e = d + 100 | 0;
            do {
                b[d >> 1] = 0;
                d = d + 2 | 0
            } while ((d | 0) < (e | 0));
            Ba(c) | 0;
            zb(a + 100 | 0) | 0;
            e = 0;
            return e | 0
        }

        function Cb(d, e, f, g, h) {
            d = d | 0;
            e = e | 0;
            f = f | 0;
            g = g | 0;
            h = h | 0;
            var j = 0, k = 0, l = 0, m = 0, n = 0, o = 0, p = 0, q = 0, r = 0, s = 0, t = 0, u = 0, v = 0, w = 0, x = 0;
            w = i;
            i = i + 96 | 0;
            s = w + 22 | 0;
            t = w;
            u = w + 44 | 0;
            Pe(d + 124 | 0, f | 0, 320) | 0;
            o = u + 22 | 0;
            p = d + 100 | 0;
            q = d + 80 | 0;
            r = d + 102 | 0;
            if ((e & -2 | 0) == 6) {
                n = 0;
                while (1) {
                    Ie(g, 702, s);
                    Ie(g, 722, t);
                    m = d + 104 + (n + 10 << 1) | 0;
                    Be(s, m, d, 40);
                    k = u;
                    j = s;
                    e = k + 22 | 0;
                    do {
                        b[k >> 1] = b[j >> 1] | 0;
                        k = k + 2 | 0;
                        j = j + 2 | 0
                    } while ((k | 0) < (e | 0));
                    k = o;
                    e = k + 22 | 0;
                    do {
                        b[k >> 1] = 0;
                        k = k + 2 | 0
                    } while ((k | 0) < (e | 0));
                    He(t, u, u, 22, o, 0);
                    e = 0;
                    k = 21;
                    do {
                        j = b[u + (k << 16 >> 16 << 1) >> 1] | 0;
                        j = Z(j, j) | 0;
                        if ((j | 0) == 1073741824) {
                            v = 7;
                            break
                        }
                        l = j << 1;
                        j = l + e | 0;
                        if ((l ^ e | 0) > -1 & (j ^ e | 0) < 0) {
                            _abort();//fix cc 精简
                        } else e = j;
                        k = k + -1 << 16 >> 16
                    } while (k << 16 >> 16 > -1);
                    if ((v | 0) == 7) {
                        v = 0;
                        c[h >> 2] = 1
                    }
                    l = e >>> 16 & 65535;
                    j = 20;
                    e = 0;
                    k = 20;
                    while (1) {
                        j = Z(b[u + (j + 1 << 1) >> 1] | 0, b[u + (j << 1) >> 1] | 0) | 0;
                        if ((j | 0) == 1073741824) {
                            v = 13;
                            break
                        }
                        x = j << 1;
                        j = x + e | 0;
                        if ((x ^ e | 0) > -1 & (j ^ e | 0) < 0) {
                            _abort();//fix cc 精简
                        } else e = j;
                        j = (k & 65535) + -1 << 16 >> 16;
                        if (j << 16 >> 16 > -1) {
                            j = j << 16 >> 16;
                            k = k + -1 | 0
                        } else break
                    }
                    if ((v | 0) == 13) {
                        v = 0;
                        c[h >> 2] = 1
                    }
                    e = e >> 16;
                    if ((e | 0) < 1) e = 0; else e = Td((e * 26214 | 0) >>> 15 & 65535, l) | 0;
                    Ab(p, d, e, 40, h);
                    e = f + (n << 1) | 0;
                    He(t, d, e, 40, q, 1);
                    Ca(r, m, e, 29491, 40, h);
                    e = (n << 16) + 2621440 | 0;
                    if ((e | 0) < 10485760) {
                        n = e >> 16;
                        g = g + 22 | 0
                    } else break
                }
                k = d + 104 | 0;
                j = d + 424 | 0;
                e = k + 20 | 0;
                do {
                    a[k >> 0] = a[j >> 0] | 0;
                    k = k + 1 | 0;
                    j = j + 1 | 0
                } while ((k | 0) < (e | 0));
                i = w;
                return
            } else {
                n = 0;
                while (1) {
                    Ie(g, 742, s);
                    Ie(g, 762, t);
                    m = d + 104 + (n + 10 << 1) | 0;
                    Be(s, m, d, 40);
                    k = u;
                    j = s;
                    e = k + 22 | 0;
                    do {
                        b[k >> 1] = b[j >> 1] | 0;
                        k = k + 2 | 0;
                        j = j + 2 | 0
                    } while ((k | 0) < (e | 0));
                    k = o;
                    e = k + 22 | 0;
                    do {
                        b[k >> 1] = 0;
                        k = k + 2 | 0
                    } while ((k | 0) < (e | 0));
                    He(t, u, u, 22, o, 0);
                    e = 0;
                    k = 21;
                    do {
                        j = b[u + (k << 16 >> 16 << 1) >> 1] | 0;
                        j = Z(j, j) | 0;
                        if ((j | 0) == 1073741824) {
                            v = 22;
                            break
                        }
                        x = j << 1;
                        j = x + e | 0;
                        if ((x ^ e | 0) > -1 & (j ^ e | 0) < 0) {
                            _abort();//fix cc 精简
                        } else e = j;
                        k = k + -1 << 16 >> 16
                    } while (k << 16 >> 16 > -1);
                    if ((v | 0) == 22) {
                        v = 0;
                        c[h >> 2] = 1
                    }
                    l = e >>> 16 & 65535;
                    j = 20;
                    e = 0;
                    k = 20;
                    while (1) {
                        j = Z(b[u + (j + 1 << 1) >> 1] | 0, b[u + (j << 1) >> 1] | 0) | 0;
                        if ((j | 0) == 1073741824) {
                            v = 28;
                            break
                        }
                        x = j << 1;
                        j = x + e | 0;
                        if ((x ^ e | 0) > -1 & (j ^ e | 0) < 0) {
                            _abort();//fix cc 精简
                        } else e = j;
                        j = (k & 65535) + -1 << 16 >> 16;
                        if (j << 16 >> 16 > -1) {
                            j = j << 16 >> 16;
                            k = k + -1 | 0
                        } else break
                    }
                    if ((v | 0) == 28) {
                        v = 0;
                        c[h >> 2] = 1
                    }
                    e = e >> 16;
                    if ((e | 0) < 1) e = 0; else e = Td((e * 26214 | 0) >>> 15 & 65535, l) | 0;
                    Ab(p, d, e, 40, h);
                    e = f + (n << 1) | 0;
                    He(t, d, e, 40, q, 1);
                    Ca(r, m, e, 29491, 40, h);
                    e = (n << 16) + 2621440 | 0;
                    if ((e | 0) < 10485760) {
                        n = e >> 16;
                        g = g + 22 | 0
                    } else break
                }
                k = d + 104 | 0;
                j = d + 424 | 0;
                e = k + 20 | 0;
                do {
                    a[k >> 0] = a[j >> 0] | 0;
                    k = k + 1 | 0;
                    j = j + 1 | 0
                } while ((k | 0) < (e | 0));
                i = w;
                return
            }
        }

        function Db(a, b) {
            a = a | 0;
            b = b | 0;
            var d = 0, e = 0;
            if (!a) {
                a = -1;
                return a | 0
            }
            c[a >> 2] = 0;
            d = Je(1764) | 0;
            if (!d) {
                a = -1;
                return a | 0
            }
            if ((Ua(d) | 0) << 16 >> 16 == 0 ? (e = d + 1748 | 0, (xb(e) | 0) << 16 >> 16 == 0) : 0) {
                Va(d, 0) | 0;
                Bb(d + 1304 | 0) | 0;
                xb(e) | 0;
                c[d + 1760 >> 2] = 0;
                c[a >> 2] = d;
                a = 0;
                return a | 0
            }
            b = c[d >> 2] | 0;
            if (!b) {
                a = -1;
                return a | 0
            }
            Ke(b);
            c[d >> 2] = 0;
            a = -1;
            return a | 0
        }

        function Eb(a) {
            a = a | 0;
            var b = 0;
            if (!a) return;
            b = c[a >> 2] | 0;
            if (!b) return;
            Ke(b);
            c[a >> 2] = 0;
            return
        }

        function Fb(a, d, f, g, h) {
            a = a | 0;
            d = d | 0;
            f = f | 0;
            g = g | 0;
            h = h | 0;
            var j = 0, k = 0, l = 0, m = 0, n = 0, o = 0, p = 0, q = 0, r = 0, s = 0, t = 0, u = 0, v = 0;
            v = i;
            i = i + 208 | 0;
            u = v + 88 | 0;
            t = v;
            s = a + 1164 | 0;
            j = c[a + 1256 >> 2] | 0;
            if ((g + -5 | 0) >>> 0 < 2) {
                _abort();//fix cc 精简
            } else {
                q = j + (d << 1) | 0;
                if ((b[q >> 1] | 0) > 0) {
                    r = c[(c[a + 1260 >> 2] | 0) + (d << 2) >> 2] | 0;
                    o = 0;
                    j = 0;
                    while (1) {
                        p = r + (o << 1) | 0;
                        m = b[p >> 1] | 0;
                        if (m << 16 >> 16 > 0) {
                            l = f;
                            n = 0;
                            k = 0;
                            while (1) {
                                k = e[l >> 1] | k << 1 & 131070;
                                n = n + 1 << 16 >> 16;
                                if (n << 16 >> 16 >= m << 16 >> 16) break; else l = l + 2 | 0
                            }
                            k = k & 65535
                        } else k = 0;
                        b[u + (o << 1) >> 1] = k;
                        j = j + 1 << 16 >> 16;
                        if (j << 16 >> 16 < (b[q >> 1] | 0)) {
                            f = f + (b[p >> 1] << 1) | 0;
                            o = j << 16 >> 16
                        } else break
                    }
                }
            }
            Wa(a, d, u, g, h, t);
            Cb(a + 1304 | 0, d, h, t, s);
            yb(a + 1748 | 0, h, 160, s);
            j = 0;
            do {
                a = h + (j << 1) | 0;
                b[a >> 1] = e[a >> 1] & 65528;
                j = j + 1 | 0
            } while ((j | 0) != 160);
            i = v;
            return
        }

        function Gb(a, f, g, h) {
            a = a | 0;
            f = f | 0;
            g = g | 0;
            h = h | 0;
            var i = 0, j = 0, k = 0;
            j = c[h + 100 >> 2] | 0;
            k = (e[(c[h + 96 >> 2] | 0) + (a << 1) >> 1] | 0) + 65535 | 0;
            h = k & 65535;
            i = h << 16 >> 16 > -1;
            if (a >>> 0 < 8) {
                if (!i) return;
                j = c[j + (a << 2) >> 2] | 0;
                i = k << 16 >> 16;
                while (1) {
                    b[g + (b[j + (i << 1) >> 1] << 1) >> 1] = (d[f + (i >> 3) >> 0] | 0) >>> (i & 7 ^ 7) & 1;
                    h = h + -1 << 16 >> 16;
                    if (h << 16 >> 16 > -1) i = h << 16 >> 16; else break
                }
                return
            } else {
                _abort();//fix cc 精简
            }
        }

        function Hb(a, b, c) {
            a = a | 0;
            b = b | 0;
            c = c | 0;
            a = vd(a, c, 31764) | 0;
            return ((sd(b) | 0 | a) << 16 >> 16 != 0) << 31 >> 31 | 0
        }

        function Ib(a, b) {
            a = a | 0;
            b = b | 0;
            wd(a);
            td(b);
            return
        }

        function Jb(d, f, g, h, j, k, l) {
            d = d | 0;
            f = f | 0;
            g = g | 0;
            h = h | 0;
            j = j | 0;
            k = k | 0;
            l = l | 0;
            var m = 0, n = 0, o = 0, p = 0, q = 0;
            q = i;
            i = i + 512 | 0;
            m = q + 8 | 0;
            n = q + 4 | 0;
            o = q;
            c[o >> 2] = 0;
            p = l << 16 >> 16 == 3;
            if (!((l & 65535) < 2 | p & 1)) {
                _abort();//fix cc 精简
            }
            xd(d, g, h, m, o);
            ud(f, c[o >> 2] | 0, n);
            h = c[n >> 2] | 0;
            if ((h | 0) != 3) {
                f = c[o >> 2] | 0;
                c[k >> 2] = f;
                if ((f | 0) == 8) {
                    _abort();//fix cc 精简
                }
            } else {
                c[k >> 2] = 15;
                f = 15
            }
            if (p) {
                tc(f, m, j, (c[d + 4 >> 2] | 0) + 2392 | 0);
                j = b[3404 + (c[k >> 2] << 16 >> 16 << 1) >> 1] | 0;
                i = q;
                return j | 0
            }
            switch (l << 16 >> 16) {
                case 0: {
                    _abort();//fix cc 精简
                }
                case 1: {
                    _abort();//fix cc 精简
                }
                default: {
                    j = -1;
                    i = q;
                    return j | 0
                }
            }
            return 0
        }

        function Kb(a, c, d, e, f, g) {
            a = a | 0;
            c = c | 0;
            d = d | 0;
            e = e | 0;
            f = f | 0;
            g = g | 0;
            var h = 0, j = 0, k = 0, l = 0, m = 0, n = 0, o = 0, p = 0, q = 0, r = 0, s = 0, t = 0, u = 0, v = 0, w = 0,
                x = 0, y = 0;
            y = i;
            i = i + 480 | 0;
            x = y;
            g = 240;
            l = f;
            k = a;
            j = x;
            h = 0;
            while (1) {
                w = ((Z(b[l >> 1] | 0, b[k >> 1] | 0) | 0) + 16384 | 0) >>> 15;
                b[j >> 1] = w;
                w = w << 16;
                h = (Z(w >> 15, w >> 16) | 0) + h | 0;
                if ((h | 0) < 0) {
                    m = 4;
                    break
                }
                g = g + -1 | 0;
                if (!((g & 65535) << 16 >> 16)) {
                    g = 0;
                    break
                } else {
                    l = l + 2 | 0;
                    k = k + 2 | 0;
                    j = j + 2 | 0
                }
            }
            if ((m | 0) == 4) {
                h = g & 65535;
                j = 240 - g | 0;
                if (!(h << 16 >> 16)) g = 0; else {
                    l = h;
                    k = f + (j << 1) | 0;
                    g = a + (j << 1) | 0;
                    h = x + (j << 1) | 0;
                    while (1) {
                        b[h >> 1] = ((Z(b[k >> 1] | 0, b[g >> 1] | 0) | 0) + 16384 | 0) >>> 15;
                        l = l + -1 << 16 >> 16;
                        if (!(l << 16 >> 16)) {
                            g = 0;
                            break
                        } else {
                            k = k + 2 | 0;
                            g = g + 2 | 0;
                            h = h + 2 | 0
                        }
                    }
                }
                do {
                    k = g & 65535;
                    g = 120;
                    j = x;
                    h = 0;
                    while (1) {
                        w = (b[j >> 1] | 0) >>> 2;
                        u = j + 2 | 0;
                        b[j >> 1] = w;
                        w = w << 16 >> 16;
                        w = Z(w, w) | 0;
                        v = (b[u >> 1] | 0) >>> 2;
                        b[u >> 1] = v;
                        v = v << 16 >> 16;
                        h = ((Z(v, v) | 0) + w << 1) + h | 0;
                        g = g + -1 << 16 >> 16;
                        if (!(g << 16 >> 16)) break; else j = j + 4 | 0
                    }
                    g = k + 4 | 0
                } while ((h | 0) < 1)
            }
            w = h + 1 | 0;
            v = (pe(w) | 0) << 16 >> 16;
            w = w << v;
            b[d >> 1] = w >>> 16;
            b[e >> 1] = (w >>> 1) - (w >> 16 << 15);
            w = x + 478 | 0;
            l = c << 16 >> 16;
            if (c << 16 >> 16 <= 0) {
                _abort();//fix cc 精简
            }
            r = x + 476 | 0;
            s = v + 1 | 0;
            t = 239 - l | 0;
            u = x + (236 - l << 1) | 0;
            c = l;
            d = d + (l << 1) | 0;
            e = e + (l << 1) | 0;
            while (1) {
                m = Z((t >>> 1) + 65535 & 65535, -2) | 0;
                k = x + (m + 236 << 1) | 0;
                m = u + (m << 1) | 0;
                f = 240 - c | 0;
                q = f + -1 | 0;
                j = x + (q << 1) | 0;
                a = q >>> 1 & 65535;
                f = x + (f + -2 << 1) | 0;
                l = Z(b[w >> 1] | 0, b[j >> 1] | 0) | 0;
                if (!(a << 16 >> 16)) {
                    m = f;
                    k = r
                } else {
                    p = r;
                    o = w;
                    while (1) {
                        h = j + -4 | 0;
                        n = o + -4 | 0;
                        l = (Z(b[p >> 1] | 0, b[f >> 1] | 0) | 0) + l | 0;
                        a = a + -1 << 16 >> 16;
                        l = (Z(b[n >> 1] | 0, b[h >> 1] | 0) | 0) + l | 0;
                        if (!(a << 16 >> 16)) break; else {
                            f = j + -6 | 0;
                            p = o + -6 | 0;
                            j = h;
                            o = n
                        }
                    }
                }
                if (q & 1) l = (Z(b[k >> 1] | 0, b[m >> 1] | 0) | 0) + l | 0;
                q = l << s;
                b[d >> 1] = q >>> 16;
                b[e >> 1] = (q >>> 1) - (q >> 16 << 15);
                if ((c & 65535) + -1 << 16 >> 16 << 16 >> 16 > 0) {
                    t = t + 1 | 0;
                    u = u + 2 | 0;
                    c = c + -1 | 0;
                    d = d + -2 | 0;
                    e = e + -2 | 0
                } else break
            }
            x = v - g | 0;
            x = x & 65535;
            i = y;
            return x | 0
        }

        function Lb(a, c, d, f, g, h, j, k) {
            a = a | 0;
            c = c | 0;
            d = d | 0;
            f = f | 0;
            g = g | 0;
            h = h | 0;
            j = j | 0;
            k = k | 0;
            var l = 0, m = 0, n = 0, o = 0, p = 0, q = 0, r = 0, s = 0, t = 0, u = 0, v = 0, w = 0, x = 0, y = 0, z = 0,
                A = 0, B = 0, C = 0, D = 0, E = 0, F = 0, G = 0, H = 0, I = 0, J = 0, K = 0;
            E = i;
            i = i + 3440 | 0;
            D = E + 3420 | 0;
            z = E + 3400 | 0;
            A = E + 3224 | 0;
            C = E;
            x = E + 3320 | 0;
            B = E + 3240 | 0;
            y = E + 24 | 0;
            hc(d, a, x, 2, k);
            rd(x, c, B, A, 5, z, 5, k);
            fc(d, B, y, k);
            pd(10, 5, 5, x, y, z, A, C, k);
            c = f;
            k = c + 80 | 0;
            do {
                b[c >> 1] = 0;
                c = c + 2 | 0
            } while ((c | 0) < (k | 0));
            b[h >> 1] = 65535;
            b[h + 2 >> 1] = 65535;
            b[h + 4 >> 1] = 65535;
            b[h + 6 >> 1] = 65535;
            b[h + 8 >> 1] = 65535;
            p = 0;
            q = C;
            r = D;
            do {
                a = b[q >> 1] | 0;
                q = q + 2 | 0;
                l = (a * 6554 | 0) >>> 15;
                m = l << 16 >> 16;
                c = f + (a << 1) | 0;
                k = b[c >> 1] | 0;
                if ((b[B + (a << 1) >> 1] | 0) > 0) {
                    b[c >> 1] = k + 4096;
                    b[r >> 1] = 8192;
                    n = l
                } else {
                    b[c >> 1] = k + 61440;
                    b[r >> 1] = -8192;
                    n = m + 8 | 0
                }
                r = r + 2 | 0;
                o = n & 65535;
                c = a - (l << 2) - m << 16 >> 16;
                l = h + (c << 1) | 0;
                k = b[l >> 1] | 0;
                a = k << 16 >> 16;
                do if (k << 16 >> 16 >= 0) {
                    m = n << 16 >> 16;
                    if (!((m ^ a) & 8)) {
                        c = h + (c + 5 << 1) | 0;
                        if ((a | 0) > (m | 0)) {
                            b[c >> 1] = k;
                            b[l >> 1] = o;
                            break
                        } else {
                            b[c >> 1] = o;
                            break
                        }
                    } else {
                        c = h + (c + 5 << 1) | 0;
                        if ((a & 7) >>> 0 > (m & 7) >>> 0) {
                            b[c >> 1] = o;
                            break
                        } else {
                            b[c >> 1] = k;

                            b[l >> 1] = o;
                            break
                        }
                    }
                } else b[l >> 1] = o; while (0);
                p = p + 1 << 16 >> 16
            } while (p << 16 >> 16 < 10);
            r = D + 2 | 0;
            p = D + 4 | 0;
            n = D + 6 | 0;
            m = D + 8 | 0;
            l = D + 10 | 0;
            c = D + 12 | 0;
            k = D + 14 | 0;
            a = D + 16 | 0;
            s = D + 18 | 0;
            t = 40;
            u = d + (0 - (b[C >> 1] | 0) << 1) | 0;
            v = d + (0 - (b[C + 2 >> 1] | 0) << 1) | 0;
            w = d + (0 - (b[C + 4 >> 1] | 0) << 1) | 0;
            x = d + (0 - (b[C + 6 >> 1] | 0) << 1) | 0;
            y = d + (0 - (b[C + 8 >> 1] | 0) << 1) | 0;
            z = d + (0 - (b[C + 10 >> 1] | 0) << 1) | 0;
            A = d + (0 - (b[C + 12 >> 1] | 0) << 1) | 0;
            B = d + (0 - (b[C + 14 >> 1] | 0) << 1) | 0;
            f = d + (0 - (b[C + 16 >> 1] | 0) << 1) | 0;
            q = d + (0 - (b[C + 18 >> 1] | 0) << 1) | 0;
            o = g;
            while (1) {
                K = (Z(b[D >> 1] | 0, b[u >> 1] | 0) | 0) >> 7;
                J = (Z(b[r >> 1] | 0, b[v >> 1] | 0) | 0) >> 7;
                I = (Z(b[p >> 1] | 0, b[w >> 1] | 0) | 0) >> 7;
                H = (Z(b[n >> 1] | 0, b[x >> 1] | 0) | 0) >> 7;
                G = (Z(b[m >> 1] | 0, b[y >> 1] | 0) | 0) >> 7;
                F = (Z(b[l >> 1] | 0, b[z >> 1] | 0) | 0) >> 7;
                C = (Z(b[c >> 1] | 0, b[A >> 1] | 0) | 0) >> 7;
                d = (Z(b[k >> 1] | 0, b[B >> 1] | 0) | 0) >>> 7;
                g = (Z(b[a >> 1] | 0, b[f >> 1] | 0) | 0) >>> 7;
                b[o >> 1] = (K + 128 + J + I + H + G + F + C + d + g + ((Z(b[s >> 1] | 0, b[q >> 1] | 0) | 0) >>> 7) | 0) >>> 8;
                t = t + -1 << 16 >> 16;
                if (!(t << 16 >> 16)) break; else {
                    u = u + 2 | 0;
                    v = v + 2 | 0;
                    w = w + 2 | 0;
                    x = x + 2 | 0;
                    y = y + 2 | 0;
                    z = z + 2 | 0;
                    A = A + 2 | 0;
                    B = B + 2 | 0;
                    f = f + 2 | 0;
                    q = q + 2 | 0;
                    o = o + 2 | 0
                }
            }
            c = 0;
            do {
                k = h + (c << 1) | 0;
                a = b[k >> 1] | 0;
                if ((c | 0) < 5) a = (e[j + ((a & 7) << 1) >> 1] | a & 8) & 65535; else a = b[j + ((a & 7) << 1) >> 1] | 0;
                b[k >> 1] = a;
                c = c + 1 | 0
            } while ((c | 0) != 10);
            i = E;
            return
        }

        function Mb(a, d, e, f, g, h, j, k) {
            a = a | 0;
            d = d | 0;
            e = e | 0;
            f = f | 0;
            g = g | 0;
            h = h | 0;
            j = j | 0;
            k = k | 0;
            var l = 0, m = 0, n = 0, o = 0, p = 0, q = 0, r = 0, s = 0, t = 0, u = 0, v = 0, w = 0, x = 0, y = 0, z = 0,
                A = 0, B = 0, C = 0, D = 0, E = 0, F = 0, G = 0, H = 0, I = 0, J = 0, K = 0, L = 0, M = 0, N = 0;
            N = i;
            i = i + 3456 | 0;
            I = N + 3448 | 0;
            G = N + 3360 | 0;
            E = N + 3368 | 0;
            p = N + 3280 | 0;
            H = N + 3200 | 0;
            F = N;
            K = (f & 65535) << 17;
            M = e << 16 >> 16;
            J = e << 16 >> 16 < 40;
            if (J) {
                f = K >> 16;
                e = M;
                do {
                    m = (Z(b[d + (e - M << 1) >> 1] | 0, f) | 0) >> 15;
                    if ((m | 0) > 32767) {
                        c[k >> 2] = 1;
                        m = 32767
                    }
                    D = d + (e << 1) | 0;
                    b[D >> 1] = Rd(b[D >> 1] | 0, m & 65535, k) | 0;
                    e = e + 1 | 0
                } while ((e & 65535) << 16 >> 16 != 40)
            }
            hc(d, a, E, 1, k);
            qd(E, H, p, 8);
            fc(d, H, F, k);
            D = G + 2 | 0;
            b[G >> 1] = 0;
            b[D >> 1] = 1;
            a = 1;
            m = 0;
            o = 1;
            p = 0;
            n = -1;
            do {
                B = b[2830 + (p << 1) >> 1] | 0;
                C = B << 16 >> 16;
                A = 0;
                do {
                    y = b[2834 + (A << 1) >> 1] | 0;
                    z = y << 16 >> 16;
                    x = a;
                    v = C;
                    u = o;
                    w = B;
                    t = n;
                    while (1) {
                        l = b[E + (v << 1) >> 1] | 0;
                        r = b[F + (v * 80 | 0) + (v << 1) >> 1] | 0;
                        e = z;
                        o = 1;
                        s = y;
                        a = y;
                        n = -1;
                        while (1) {
                            f = Rd(l, b[E + (e << 1) >> 1] | 0, k) | 0;
                            f = f << 16 >> 16;
                            f = (Z(f, f) | 0) >>> 15;
                            q = (b[F + (v * 80 | 0) + (e << 1) >> 1] << 15) + 32768 + ((b[F + (e * 80 | 0) + (e << 1) >> 1] | 0) + r << 14) | 0;
                            if (((Z(f << 16 >> 16, o << 16 >> 16) | 0) - (Z(q >> 16, n << 16 >> 16) | 0) << 1 | 0) > 0) {
                                o = q >>> 16 & 65535;
                                a = s;
                                n = f & 65535
                            }
                            q = e + 5 | 0;
                            s = q & 65535;
                            if (s << 16 >> 16 >= 40) break; else e = q << 16 >> 16
                        }
                        if (((Z(n << 16 >> 16, u << 16 >> 16) | 0) - (Z(o << 16 >> 16, t << 16 >> 16) | 0) << 1 | 0) > 0) {
                            b[G >> 1] = w;
                            b[D >> 1] = a;
                            m = w
                        } else {
                            a = x;
                            o = u;
                            n = t
                        }
                        q = v + 5 | 0;
                        w = q & 65535;
                        if (w << 16 >> 16 >= 40) break; else {
                            x = a;
                            v = q << 16 >> 16;
                            u = o;
                            t = n
                        }
                    }
                    A = A + 1 | 0
                } while ((A | 0) != 4);
                p = p + 1 | 0
            } while ((p | 0) != 2);
            r = a;
            s = m;
            f = g;
            e = f + 80 | 0;
            do {
                b[f >> 1] = 0;
                f = f + 2 | 0
            } while ((f | 0) < (e | 0));
            o = s;
            e = 0;
            q = 0;
            f = 0;
            while (1) {
                m = o << 16 >> 16;
                l = b[H + (m << 1) >> 1] | 0;
                a = (m * 6554 | 0) >>> 15;
                o = a << 16;
                p = o >> 15;
                n = m - (p + (a << 3) << 16 >> 17) | 0;
                switch (n << 16 >> 16 | 0) {
                    case 0: {
                        p = o >> 10;
                        a = 1;
                        break
                    }
                    case 1: {
                        if (!((e & 65535) << 16 >> 16)) a = 0; else {
                            p = a << 22 >> 16 | 16;
                            a = 1
                        }
                        break
                    }
                    case 2: {
                        p = a << 22 >> 16 | 32;
                        a = 1;
                        break
                    }
                    case 3: {
                        p = a << 17 >> 16 | 1;
                        a = 0;
                        break
                    }
                    case 4: {
                        p = a << 22 >> 16 | 48;
                        a = 1;
                        break
                    }
                    default: {
                        p = a;
                        a = n & 65535
                    }
                }
                p = p & 65535;
                n = g + (m << 1) | 0;
                if (l << 16 >> 16 > 0) {
                    b[n >> 1] = 8191;
                    b[I + (e << 1) >> 1] = 32767;
                    m = a << 16 >> 16;
                    if (a << 16 >> 16 < 0) {
                        _abort();//fix cc 精简
                    } else {
                        F = 1 << m;
                        m = (F << 16 >> 16 >> m | 0) == 1 ? F & 65535 : 32767
                    }
                    f = Rd(f, m, k) | 0
                } else {
                    b[n >> 1] = -8192;
                    b[I + (e << 1) >> 1] = -32768
                }
                m = Rd(q, p, k) | 0;
                e = e + 1 | 0;
                if ((e | 0) == 2) {
                    q = m;
                    break
                }
                o = b[G + (e << 1) >> 1] | 0;
                q = m
            }
            b[j >> 1] = f;
            p = I + 2 | 0;
            o = b[I >> 1] | 0;
            a = 0;
            n = d + (0 - (s << 16 >> 16) << 1) | 0;
            m = d + (0 - (r << 16 >> 16) << 1) | 0;
            do {
                f = Z(b[n >> 1] | 0, o) | 0;
                n = n + 2 | 0;
                if ((f | 0) != 1073741824 ? (L = f << 1, !((f | 0) > 0 & (L | 0) < 0)) : 0) l = L; else {
                    c[k >> 2] = 1;
                    l = 2147483647
                }
                e = Z(b[p >> 1] | 0, b[m >> 1] | 0) | 0;
                m = m + 2 | 0;
                if ((e | 0) != 1073741824) {
                    f = (e << 1) + l | 0;
                    if ((e ^ l | 0) > 0 & (f ^ l | 0) < 0) {
                        c[k >> 2] = 1;
                        f = (l >>> 31) + 2147483647 | 0
                    }
                } else {
                    c[k >> 2] = 1;
                    f = 2147483647
                }
                b[h + (a << 1) >> 1] = Ce(f, k) | 0;
                a = a + 1 | 0
            } while ((a | 0) != 40);
            if (!J) {
                i = N;
                return q | 0
            }
            e = K >> 16;
            f = M;
            do {
                l = (Z(b[g + (f - M << 1) >> 1] | 0, e) | 0) >> 15;
                if ((l | 0) > 32767) {
                    c[k >> 2] = 1;
                    l = 32767
                }
                h = g + (f << 1) | 0;
                b[h >> 1] = Rd(b[h >> 1] | 0, l & 65535, k) | 0;
                f = f + 1 | 0
            } while ((f & 65535) << 16 >> 16 != 40);
            i = N;
            return q | 0
        }

        function Nb(a, d, e, f, g, h, j, k, l, m) {
            a = a | 0;
            d = d | 0;
            e = e | 0;
            f = f | 0;
            g = g | 0;
            h = h | 0;
            j = j | 0;
            k = k | 0;
            l = l | 0;
            m = m | 0;
            var n = 0, o = 0, p = 0, q = 0, r = 0, s = 0, t = 0, u = 0, v = 0, w = 0, x = 0;
            x = i;
            i = i + 3456 | 0;
            r = x + 3360 | 0;
            s = x + 3368 | 0;
            t = x + 3280 | 0;
            u = x + 3200 | 0;
            v = x;
            w = g << 16 >> 16;
            p = w << 1;
            if ((p | 0) == (w << 17 >> 16 | 0)) q = p; else {
                c[m >> 2] = 1;
                q = g << 16 >> 16 > 0 ? 32767 : -32768
            }
            w = f << 16 >> 16;
            n = f << 16 >> 16 < 40;
            if (n) {
                g = q << 16 >> 16;
                o = w;
                do {
                    f = e + (o << 1) | 0;
                    p = (Z(b[e + (o - w << 1) >> 1] | 0, g) | 0) >> 15;
                    if ((p | 0) > 32767) {
                        c[m >> 2] = 1;
                        p = 32767
                    }
                    b[f >> 1] = Rd(b[f >> 1] | 0, p & 65535, m) | 0;
                    o = o + 1 | 0
                } while ((o & 65535) << 16 >> 16 != 40)
            }
            hc(e, d, s, 1, m);
            qd(s, u, t, 8);
            fc(e, u, v, m);
            Ob(a, s, v, l, r);
            p = Pb(a, r, u, h, e, j, k, m) | 0;
            if (!n) {
                i = x;
                return p | 0
            }
            o = q << 16 >> 16;
            g = w;
            do {
                f = h + (g << 1) | 0;
                n = (Z(b[h + (g - w << 1) >> 1] | 0, o) | 0) >> 15;
                if ((n | 0) > 32767) {
                    c[m >> 2] = 1;
                    n = 32767
                }
                b[f >> 1] = Rd(b[f >> 1] | 0, n & 65535, m) | 0;
                g = g + 1 | 0
            } while ((g & 65535) << 16 >> 16 != 40);
            i = x;
            return p | 0
        }

        function Ob(a, c, d, f, g) {
            a = a | 0;
            c = c | 0;
            d = d | 0;
            f = f | 0;
            g = g | 0;
            var h = 0, i = 0, j = 0, k = 0, l = 0, m = 0, n = 0, o = 0, p = 0, q = 0, r = 0, s = 0, t = 0, u = 0, v = 0,
                w = 0, x = 0;
            x = g + 2 | 0;
            b[g >> 1] = 0;
            b[x >> 1] = 1;
            v = a << 16 >> 16 << 1;
            h = 1;
            w = 0;
            a = -1;
            do {
                u = (w << 3) + v << 16 >> 16;
                k = b[f + (u << 1) >> 1] | 0;
                u = b[f + ((u | 1) << 1) >> 1] | 0;
                i = k << 16 >> 16;
                a:do if (k << 16 >> 16 < 40) {
                    t = u << 16 >> 16;
                    if (u << 16 >> 16 < 40) s = h; else while (1) {
                        _abort();//fix cc 精简
                    }
                    while (1) {
                        q = b[d + (i * 80 | 0) + (i << 1) >> 1] | 0;
                        p = e[c + (i << 1) >> 1] | 0;
                        o = t;
                        h = 1;
                        r = u;
                        j = u;
                        l = -1;
                        while (1) {
                            n = (e[c + (o << 1) >> 1] | 0) + p << 16 >> 16;
                            n = (Z(n, n) | 0) >>> 15;
                            m = (b[d + (i * 80 | 0) + (o << 1) >> 1] << 15) + 32768 + ((b[d + (o * 80 | 0) + (o << 1) >> 1] | 0) + q << 14) | 0;
                            if (((Z(n << 16 >> 16, h << 16 >> 16) | 0) - (Z(m >> 16, l << 16 >> 16) | 0) << 1 | 0) > 0) {
                                h = m >>> 16 & 65535;
                                j = r;
                                l = n & 65535
                            }
                            m = o + 5 | 0;
                            r = m & 65535;
                            if (r << 16 >> 16 >= 40) break; else o = m << 16 >> 16
                        }
                        if (((Z(l << 16 >> 16, s << 16 >> 16) | 0) - (Z(h << 16 >> 16, a << 16 >> 16) | 0) << 1 | 0) > 0) {
                            b[g >> 1] = k;
                            b[x >> 1] = j;
                            a = l
                        } else h = s;
                        i = i + 5 | 0;
                        k = i & 65535;
                        if (k << 16 >> 16 >= 40) break; else {
                            i = i << 16 >> 16;
                            s = h
                        }
                    }
                } while (0);
                w = w + 1 | 0
            } while ((w | 0) != 2);
            return
        }

        function Pb(a, d, e, f, g, h, i, j) {
            a = a | 0;
            d = d | 0;
            e = e | 0;
            f = f | 0;
            g = g | 0;
            h = h | 0;
            i = i | 0;
            j = j | 0;
            var k = 0, l = 0, m = 0, n = 0, o = 0, p = 0;
            k = f;
            l = k + 80 | 0;
            do {
                b[k >> 1] = 0;
                k = k + 2 | 0
            } while ((k | 0) < (l | 0));
            k = b[d >> 1] | 0;
            o = (k * 6554 | 0) >>> 15;
            l = o << 16 >> 16;
            n = (748250 >>> ((k + (Z(l, -5) | 0) << 16 >> 16) + ((a << 16 >> 16) * 5 | 0) | 0) & 1 | 0) == 0;
            m = (b[e + (k << 1) >> 1] | 0) > 0;
            p = m ? 32767 : -32768;
            b[f + (k << 1) >> 1] = m ? 8191 : -8192;
            k = d + 2 | 0;
            a = b[k >> 1] | 0;
            f = f + (a << 1) | 0;
            if ((b[e + (a << 1) >> 1] | 0) > 0) {
                b[f >> 1] = 8191;
                e = 32767;
                f = (m & 1 | 2) & 65535
            } else {
                b[f >> 1] = -8192;
                e = -32768;
                f = m & 1
            }
            o = ((a * 6554 | 0) >>> 15 << 3) + (n ? o : l + 64 | 0) & 65535;
            b[i >> 1] = f;
            n = 0;
            m = g + (0 - (b[d >> 1] | 0) << 1) | 0;
            f = g + (0 - (b[k >> 1] | 0) << 1) | 0;
            do {
                k = Z(p, b[m >> 1] | 0) | 0;
                m = m + 2 | 0;
                if ((k | 0) == 1073741824) {
                    c[j >> 2] = 1;
                    a = 2147483647
                } else a = k << 1;
                l = Z(e, b[f >> 1] | 0) | 0;
                f = f + 2 | 0;
                if ((l | 0) != 1073741824) {
                    k = (l << 1) + a | 0;
                    if ((l ^ a | 0) > 0 & (k ^ a | 0) < 0) {
                        c[j >> 2] = 1;
                        k = (a >>> 31) + 2147483647 | 0
                    }
                } else {
                    c[j >> 2] = 1;
                    k = 2147483647
                }
                b[h + (n << 1) >> 1] = Ce(k, j) | 0;
                n = n + 1 | 0
            } while ((n | 0) != 40);
            return o | 0
        }

        function Qb(a, d, f, g, h, j, k, l) {
            a = a | 0;
            d = d | 0;
            f = f | 0;
            g = g | 0;
            h = h | 0;
            j = j | 0;
            k = k | 0;
            l = l | 0;
            var m = 0, n = 0, o = 0, p = 0, q = 0, r = 0, s = 0, t = 0, u = 0, v = 0, w = 0, x = 0, y = 0, z = 0, A = 0,
                B = 0, C = 0, D = 0, E = 0, F = 0, G = 0, H = 0, I = 0, J = 0, K = 0, L = 0, M = 0, N = 0, O = 0, P = 0,
                Q = 0, R = 0, S = 0, T = 0, U = 0;
            U = i;
            i = i + 3440 | 0;
            M = U + 3360 | 0;
            N = U + 3280 | 0;
            P = U + 3200 | 0;
            O = U;
            R = (g & 65535) << 17;
            T = f << 16 >> 16;
            Q = f << 16 >> 16 < 40;
            if (Q) {
                f = R >> 16;
                m = T;
                do {
                    g = (Z(b[d + (m - T << 1) >> 1] | 0, f) | 0) >> 15;
                    if ((g | 0) > 32767) {
                        c[l >> 2] = 1;
                        g = 32767
                    }
                    L = d + (m << 1) | 0;
                    b[L >> 1] = Rd(b[L >> 1] | 0, g & 65535, l) | 0;
                    m = m + 1 | 0
                } while ((m & 65535) << 16 >> 16 != 40)
            }
            hc(d, a, M, 1, l);
            qd(M, P, N, 6);
            fc(d, P, O, l);
            L = 1;
            n = 2;
            o = 1;
            g = 0;
            m = 1;
            a = -1;
            p = 1;
            while (1) {
                K = 2;
                s = 2;
                while (1) {
                    H = 0;
                    I = 0;
                    J = p;
                    G = s;
                    while (1) {
                        if (I << 16 >> 16 < 40) {
                            C = J << 16 >> 16;
                            D = J << 16 >> 16 < 40;
                            E = G << 16 >> 16;
                            F = G << 16 >> 16 < 40;
                            A = I << 16 >> 16;
                            B = I;
                            while (1) {
                                if ((b[N + (A << 1) >> 1] | 0) > -1) {
                                    x = b[O + (A * 80 | 0) + (A << 1) >> 1] | 0;
                                    if (D) {
                                        y = e[M + (A << 1) >> 1] | 0;
                                        w = C;
                                        r = 1;
                                        z = J;
                                        f = J;
                                        s = 0;
                                        q = -1;
                                        while (1) {
                                            u = (e[M + (w << 1) >> 1] | 0) + y | 0;
                                            v = u << 16 >> 16;
                                            v = (Z(v, v) | 0) >>> 15;
                                            t = (b[O + (A * 80 | 0) + (w << 1) >> 1] << 15) + 32768 + ((b[O + (w * 80 | 0) + (w << 1) >> 1] | 0) + x << 14) | 0;
                                            if (((Z(v << 16 >> 16, r << 16 >> 16) | 0) - (Z(t >> 16, q << 16 >> 16) | 0) << 1 | 0) > 0) {
                                                r = t >>> 16 & 65535;
                                                f = z;
                                                s = u & 65535;
                                                q = v & 65535
                                            }
                                            t = w + 5 | 0;
                                            z = t & 65535;
                                            if (z << 16 >> 16 >= 40) break; else w = t << 16 >> 16
                                        }
                                    } else {
                                        r = 1;
                                        f = J;
                                        s = 0
                                    }
                                    if (F) {
                                        y = s & 65535;
                                        z = f << 16 >> 16;
                                        w = (r << 16 >> 16 << 14) + 32768 | 0;
                                        v = E;
                                        s = 1;
                                        x = G;
                                        q = G;
                                        r = -1;
                                        while (1) {
                                            u = (e[M + (v << 1) >> 1] | 0) + y << 16 >> 16;
                                            u = (Z(u, u) | 0) >>> 15;
                                            t = w + (b[O + (v * 80 | 0) + (v << 1) >> 1] << 12) + ((b[O + (A * 80 | 0) + (v << 1) >> 1] | 0) + (b[O + (z * 80 | 0) + (v << 1) >> 1] | 0) << 13) | 0;
                                            if (((Z(u << 16 >> 16, s << 16 >> 16) | 0) - (Z(t >> 16, r << 16 >> 16) | 0) << 1 | 0) > 0) {
                                                s = t >>> 16 & 65535;
                                                q = x;
                                                r = u & 65535
                                            }
                                            t = v + 5 | 0;
                                            x = t & 65535;
                                            if (x << 16 >> 16 >= 40) {
                                                w = s;
                                                v = r;
                                                break
                                            } else v = t << 16 >> 16
                                        }
                                    } else {
                                        w = 1;
                                        q = G;
                                        v = -1
                                    }
                                    s = Z(v << 16 >> 16, m << 16 >> 16) | 0;
                                    if ((s | 0) == 1073741824) {
                                        _abort();//fix cc 精简
                                    } else t = s << 1;
                                    s = Z(w << 16 >> 16, a << 16 >> 16) | 0;
                                    if ((s | 0) == 1073741824) {
                                        _abort();//fix cc 精简
                                    } else r = s << 1;
                                    s = t - r | 0;
                                    if (((s ^ t) & (r ^ t) | 0) < 0) {
                                        _abort();//fix cc 精简
                                    }
                                    z = (s | 0) > 0;
                                    n = z ? q : n;
                                    o = z ? f : o;
                                    g = z ? B : g;
                                    m = z ? w : m;
                                    a = z ? v : a
                                }
                                s = A + 5 | 0;
                                B = s & 65535;
                                if (B << 16 >> 16 >= 40) break; else A = s << 16 >> 16
                            }
                        }
                        H = H + 1 << 16 >> 16;
                        if (H << 16 >> 16 >= 3) break; else {
                            F = G;
                            G = J;
                            J = I;
                            I = F
                        }
                    }
                    f = K + 2 | 0;
                    s = f & 65535;
                    if (s << 16 >> 16 >= 5) break; else K = f & 65535
                }
                f = L + 2 | 0;
                p = f & 65535;
                if (p << 16 >> 16 < 4) L = f & 65535; else {
                    s = n;
                    n = o;
                    break
                }
            }
            f = h;
            m = f + 80 | 0;
            do {
                b[f >> 1] = 0;
                f = f + 2 | 0
            } while ((f | 0) < (m | 0));
            v = g << 16 >> 16;
            a = b[P + (v << 1) >> 1] | 0;
            g = (v * 6554 | 0) >>> 15;
            f = g << 16;
            m = v - (((f >> 16) * 327680 | 0) >>> 16) | 0;
            switch (m << 16 >> 16 | 0) {
                case 1: {
                    g = f >> 12;
                    break
                }
                case 2: {
                    g = f >> 8;
                    m = 2;
                    break
                }
                case 3: {
                    g = g << 20 >> 16 | 8;
                    m = 1;
                    break
                }
                case 4: {
                    g = g << 24 >> 16 | 128;
                    m = 2;
                    break
                }
                default: {
                }
            }
            f = h + (v << 1) | 0;
            if (a << 16 >> 16 > 0) {
                b[f >> 1] = 8191;
                z = 32767;
                o = 65536 << (m << 16 >> 16) >>> 16 & 65535
            } else {
                b[f >> 1] = -8192;
                z = -32768;
                o = 0
            }
            t = n << 16 >> 16;
            n = b[P + (t << 1) >> 1] | 0;
            f = (t * 6554 | 0) >>> 15;
            m = f << 16;
            a = t - (((m >> 16) * 327680 | 0) >>> 16) | 0;
            switch (a << 16 >> 16 | 0) {
                case 1: {
                    f = m >> 12;
                    break
                }
                case 2: {
                    f = m >> 8;
                    a = 2;
                    break
                }
                case 3: {
                    f = f << 20 >> 16 | 8;
                    a = 1;
                    break
                }
                case 4: {
                    f = f << 24 >> 16 | 128;
                    a = 2;
                    break
                }
                default: {
                }
            }
            m = h + (t << 1) | 0;
            if (n << 16 >> 16 > 0) {
                b[m >> 1] = 8191;
                u = 32767;
                o = (65536 << (a << 16 >> 16) >>> 16) + (o & 65535) & 65535
            } else {
                b[m >> 1] = -8192;
                u = -32768
            }
            p = f + g | 0;
            r = s << 16 >> 16;
            n = b[P + (r << 1) >> 1] | 0;
            g = (r * 6554 | 0) >>> 15;
            f = g << 16;
            m = r - (((f >> 16) * 327680 | 0) >>> 16) | 0;
            switch (m << 16 >> 16 | 0) {
                case 1: {
                    f = f >> 12;
                    break
                }
                case 2: {
                    f = f >> 8;
                    m = 2;
                    break
                }
                case 3: {
                    f = g << 20 >> 16 | 8;
                    m = 1;
                    break
                }
                case 4: {
                    f = g << 24 >> 16 | 128;
                    m = 2;
                    break
                }
                default:
                    f = g
            }
            g = h + (r << 1) | 0;
            if (n << 16 >> 16 > 0) {
                b[g >> 1] = 8191;
                s = 32767;
                g = (65536 << (m << 16 >> 16) >>> 16) + (o & 65535) & 65535
            } else {
                b[g >> 1] = -8192;
                s = -32768;
                g = o
            }
            q = p + f | 0;
            b[k >> 1] = g;
            o = 0;
            p = d + (0 - v << 1) | 0;
            a = d + (0 - t << 1) | 0;
            n = d + (0 - r << 1) | 0;
            do {
                g = Z(b[p >> 1] | 0, z) | 0;
                p = p + 2 | 0;
                if ((g | 0) != 1073741824 ? (S = g << 1, !((g | 0) > 0 & (S | 0) < 0)) : 0) m = S; else {
                    c[l >> 2] = 1;
                    m = 2147483647
                }
                g = Z(b[a >> 1] | 0, u) | 0;
                a = a + 2 | 0;
                if ((g | 0) != 1073741824) {
                    f = (g << 1) + m | 0;
                    if ((g ^ m | 0) > 0 & (f ^ m | 0) < 0) {
                        c[l >> 2] = 1;
                        f = (m >>> 31) + 2147483647 | 0
                    }
                } else {
                    c[l >> 2] = 1;
                    f = 2147483647
                }
                m = Z(b[n >> 1] | 0, s) | 0;
                n = n + 2 | 0;
                if ((m | 0) != 1073741824) {
                    g = (m << 1) + f | 0;
                    if ((m ^ f | 0) > 0 & (g ^ f | 0) < 0) {
                        c[l >> 2] = 1;
                        g = (f >>> 31) + 2147483647 | 0
                    }
                } else {
                    c[l >> 2] = 1;
                    g = 2147483647
                }
                b[j + (o << 1) >> 1] = Ce(g, l) | 0;
                o = o + 1 | 0
            } while ((o | 0) != 40);
            g = q & 65535;
            if (!Q) {
                i = U;
                return g | 0
            }
            m = R >> 16;
            f = T;
            do {
                a = (Z(b[h + (f - T << 1) >> 1] | 0, m) | 0) >> 15;
                if ((a | 0) > 32767) {
                    c[l >> 2] = 1;
                    a = 32767
                }
                j = h + (f << 1) | 0;
                b[j >> 1] = Rd(b[j >> 1] | 0, a & 65535, l) | 0;
                f = f + 1 | 0
            } while ((f & 65535) << 16 >> 16 != 40);
            i = U;
            return g | 0
        }

        function Rb(a, d, f, g, h, j, k, l, m) {
            a = a | 0;
            d = d | 0;
            f = f | 0;
            g = g | 0;
            h = h | 0;
            j = j | 0;
            k = k | 0;
            l = l | 0;
            m = m | 0;
            var n = 0, o = 0, p = 0, q = 0, r = 0, s = 0, t = 0, u = 0, v = 0, w = 0, x = 0, y = 0, z = 0, A = 0, B = 0,
                C = 0, D = 0, E = 0, F = 0, G = 0, H = 0, I = 0, J = 0, K = 0, L = 0, M = 0, N = 0, O = 0, P = 0, Q = 0,
                R = 0, S = 0, T = 0, U = 0, V = 0, W = 0, X = 0, Y = 0, _ = 0, $ = 0, aa = 0, ba = 0, ca = 0, da = 0;
            da = i;
            i = i + 3456 | 0;
            _ = da + 3448 | 0;
            X = da + 3360 | 0;
            U = da + 3368 | 0;
            V = da + 3280 | 0;
            Y = da + 3200 | 0;
            W = da;
            aa = (g & 65535) << 17;
            ca = f << 16 >> 16;
            $ = f << 16 >> 16 < 40;
            if ($) {
                f = aa >> 16;
                n = ca;
                do {
                    g = (Z(b[d + (n - ca << 1) >> 1] | 0, f) | 0) >> 15;
                    if ((g | 0) > 32767) {
                        c[m >> 2] = 1;
                        g = 32767
                    }
                    T = d + (n << 1) | 0;
                    b[T >> 1] = Rd(b[T >> 1] | 0, g & 65535, m) | 0;
                    n = n + 1 | 0
                } while ((n & 65535) << 16 >> 16 != 40)
            }
            hc(d, a, U, 1, m);
            qd(U, Y, V, 4);
            fc(d, Y, W, m);
            R = X + 2 | 0;
            b[X >> 1] = 0;
            S = X + 4 | 0;
            b[R >> 1] = 1;
            T = X + 6 | 0;
            b[S >> 1] = 2;
            b[T >> 1] = 3;
            r = 3;
            p = 2;
            o = 1;
            g = 0;
            f = 1;
            n = -1;
            q = 3;
            do {
                M = 0;
                N = 0;
                O = q;
                P = 1;
                Q = 2;
                while (1) {
                    if (N << 16 >> 16 < 40) {
                        G = P << 16 >> 16;
                        H = P << 16 >> 16 < 40;
                        I = Q << 16 >> 16;
                        J = Q << 16 >> 16 < 40;
                        K = O << 16 >> 16;
                        L = O << 16 >> 16 < 40;
                        F = N << 16 >> 16;
                        E = p;
                        C = o;
                        B = f;
                        D = N;
                        while (1) {
                            if ((b[V + (F << 1) >> 1] | 0) > -1) {
                                t = b[W + (F * 80 | 0) + (F << 1) >> 1] | 0;
                                if (H) {
                                    s = e[U + (F << 1) >> 1] | 0;
                                    u = G;
                                    z = 1;
                                    p = P;
                                    o = P;
                                    x = 0;
                                    y = -1;
                                    while (1) {
                                        w = (e[U + (u << 1) >> 1] | 0) + s | 0;
                                        v = w << 16 >> 16;
                                        v = (Z(v, v) | 0) >>> 15;
                                        A = (b[W + (F * 80 | 0) + (u << 1) >> 1] << 15) + 32768 + ((b[W + (u * 80 | 0) + (u << 1) >> 1] | 0) + t << 14) | 0;
                                        if (((Z(v << 16 >> 16, z << 16 >> 16) | 0) - (Z(A >> 16, y << 16 >> 16) | 0) << 1 | 0) > 0) {
                                            z = A >>> 16 & 65535;
                                            o = p;
                                            x = w & 65535;
                                            y = v & 65535
                                        }
                                        A = u + 5 | 0;
                                        p = A & 65535;
                                        if (p << 16 >> 16 >= 40) break; else u = A << 16 >> 16
                                    }
                                } else {
                                    z = 1;
                                    o = P;
                                    x = 0
                                }
                                if (J) {
                                    f = x & 65535;
                                    a = o << 16 >> 16;
                                    t = (z << 16 >> 16 << 14) + 32768 | 0;
                                    u = I;
                                    A = 1;
                                    s = Q;
                                    p = Q;
                                    y = 0;
                                    x = -1;
                                    while (1) {
                                        w = (e[U + (u << 1) >> 1] | 0) + f | 0;
                                        v = w << 16 >> 16;
                                        v = (Z(v, v) | 0) >>> 15;
                                        z = t + (b[W + (u * 80 | 0) + (u << 1) >> 1] << 12) + ((b[W + (F * 80 | 0) + (u << 1) >> 1] | 0) + (b[W + (a * 80 | 0) + (u << 1) >> 1] | 0) << 13) | 0;
                                        if (((Z(v << 16 >> 16, A << 16 >> 16) | 0) - (Z(z >> 16, x << 16 >> 16) | 0) << 1 | 0) > 0) {
                                            A = z >>> 16 & 65535;
                                            p = s;
                                            y = w & 65535;
                                            x = v & 65535
                                        }
                                        z = u + 5 | 0;
                                        s = z & 65535;
                                        if (s << 16 >> 16 >= 40) break; else u = z << 16 >> 16
                                    }
                                } else {
                                    A = 1;
                                    p = Q;
                                    y = 0
                                }
                                if (L) {
                                    t = y & 65535;
                                    s = p << 16 >> 16;
                                    a = o << 16 >> 16;
                                    v = (A & 65535) << 16 | 32768;
                                    w = K;
                                    f = 1;
                                    u = O;
                                    z = O;
                                    A = -1;
                                    while (1) {
                                        x = (e[U + (w << 1) >> 1] | 0) + t << 16 >> 16;
                                        x = (Z(x, x) | 0) >>> 15;
                                        y = (b[W + (w * 80 | 0) + (w << 1) >> 1] << 12) + v + ((b[W + (a * 80 | 0) + (w << 1) >> 1] | 0) + (b[W + (s * 80 | 0) + (w << 1) >> 1] | 0) + (b[W + (F * 80 | 0) + (w << 1) >> 1] | 0) << 13) | 0;
                                        if (((Z(x << 16 >> 16, f << 16 >> 16) | 0) - (Z(y >> 16, A << 16 >> 16) | 0) << 1 | 0) > 0) {
                                            f = y >>> 16 & 65535;
                                            z = u;
                                            A = x & 65535
                                        }
                                        y = w + 5 | 0;
                                        u = y & 65535;
                                        if (u << 16 >> 16 >= 40) break; else w = y << 16 >> 16
                                    }
                                } else {
                                    f = 1;
                                    z = O;
                                    A = -1
                                }
                                if (((Z(A << 16 >> 16, B << 16 >> 16) | 0) - (Z(f << 16 >> 16, n << 16 >> 16) | 0) << 1 | 0) > 0) {
                                    b[X >> 1] = D;
                                    b[R >> 1] = o;
                                    b[S >> 1] = p;
                                    b[T >> 1] = z;
                                    r = z;
                                    g = D;
                                    n = A
                                } else {
                                    p = E;
                                    o = C;
                                    f = B
                                }
                            } else {
                                p = E;
                                o = C;
                                f = B
                            }
                            w = F + 5 | 0;
                            D = w & 65535;
                            if (D << 16 >> 16 >= 40) break; else {
                                F = w << 16 >> 16;
                                E = p;
                                C = o;
                                B = f
                            }
                        }
                    }
                    M = M + 1 << 16 >> 16;
                    if (M << 16 >> 16 >= 4) break; else {
                        K = Q;
                        L = O;
                        Q = P;
                        P = N;
                        O = K;
                        N = L
                    }
                }
                q = q + 1 << 16 >> 16
            } while (q << 16 >> 16 < 5);
            A = r;
            z = p;
            y = o;
            x = g;
            g = h;
            f = g + 80 | 0;
            do {
                b[g >> 1] = 0;
                g = g + 2 | 0
            } while ((g | 0) < (f | 0));
            a = x;
            f = 0;
            n = 0;
            g = 0;
            while (1) {
                p = a << 16 >> 16;
                q = b[Y + (p << 1) >> 1] | 0;
                a = p * 13108 >> 16;
                o = p - ((a * 327680 | 0) >>> 16) | 0;
                a = b[l + (a << 1) >> 1] | 0;
                switch (o << 16 >> 16 | 0) {
                    case 1: {
                        r = a << 16 >> 16 << 3 & 65535;
                        break
                    }
                    case 2: {
                        r = a << 16 >> 16 << 6 & 65535;
                        break
                    }
                    case 3: {
                        r = a << 16 >> 16 << 10 & 65535;
                        break
                    }
                    case 4: {
                        r = ((a & 65535) << 10 | 512) & 65535;
                        o = 3;
                        break
                    }
                    default:
                        r = a
                }
                a = h + (p << 1) | 0;
                if (q << 16 >> 16 > 0) {
                    b[a >> 1] = 8191;
                    a = 32767;
                    g = (65536 << (o << 16 >> 16) >>> 16) + (g & 65535) & 65535
                } else {
                    b[a >> 1] = -8192;
                    a = -32768
                }
                b[_ + (f << 1) >> 1] = a;
                n = (r & 65535) + (n & 65535) | 0;
                f = f + 1 | 0;
                if ((f | 0) == 4) {
                    w = n;
                    break
                }
                a = b[X + (f << 1) >> 1] | 0
            }
            b[k >> 1] = g;
            t = _ + 2 | 0;
            u = _ + 4 | 0;
            v = _ + 6 | 0;
            a = b[_ >> 1] | 0;
            s = 0;
            o = d + (0 - (x << 16 >> 16) << 1) | 0;
            p = d + (0 - (y << 16 >> 16) << 1) | 0;
            q = d + (0 - (z << 16 >> 16) << 1) | 0;
            r = d + (0 - (A << 16 >> 16) << 1) | 0;
            do {
                g = Z(b[o >> 1] | 0, a) | 0;
                o = o + 2 | 0;
                if ((g | 0) != 1073741824 ? (ba = g << 1, !((g | 0) > 0 & (ba | 0) < 0)) : 0) n = ba; else {
                    c[m >> 2] = 1;
                    n = 2147483647
                }
                g = Z(b[t >> 1] | 0, b[p >> 1] | 0) | 0;
                p = p + 2 | 0;
                if ((g | 0) != 1073741824) {
                    f = (g << 1) + n | 0;
                    if ((g ^ n | 0) > 0 & (f ^ n | 0) < 0) {
                        c[m >> 2] = 1;
                        f = (n >>> 31) + 2147483647 | 0
                    }
                } else {
                    c[m >> 2] = 1;
                    f = 2147483647
                }
                g = Z(b[u >> 1] | 0, b[q >> 1] | 0) | 0;
                q = q + 2 | 0;
                if ((g | 0) != 1073741824) {
                    n = (g << 1) + f | 0;
                    if ((g ^ f | 0) > 0 & (n ^ f | 0) < 0) {
                        c[m >> 2] = 1;
                        n = (f >>> 31) + 2147483647 | 0
                    }
                } else {
                    c[m >> 2] = 1;
                    n = 2147483647
                }
                f = Z(b[v >> 1] | 0, b[r >> 1] | 0) | 0;
                r = r + 2 | 0;
                if ((f | 0) != 1073741824) {
                    g = (f << 1) + n | 0;
                    if ((f ^ n | 0) > 0 & (g ^ n | 0) < 0) {
                        c[m >> 2] = 1;
                        g = (n >>> 31) + 2147483647 | 0
                    }
                } else {
                    c[m >> 2] = 1;
                    g = 2147483647
                }
                b[j + (s << 1) >> 1] = Ce(g, m) | 0;
                s = s + 1 | 0
            } while ((s | 0) != 40);
            g = w & 65535;
            if (((ca << 16) + -2621440 | 0) > -1 | $ ^ 1) {
                i = da;
                return g | 0
            }
            n = aa >> 16;
            f = ca;
            do {
                a = (Z(b[h + (f - ca << 1) >> 1] | 0, n) | 0) >> 15;
                if ((a | 0) > 32767) {
                    c[m >> 2] = 1;
                    a = 32767
                }
                j = h + (f << 1) | 0;
                b[j >> 1] = Rd(b[j >> 1] | 0, a & 65535, m) | 0;
                f = f + 1 | 0
            } while ((f & 65535) << 16 >> 16 != 40);
            i = da;
            return g | 0
        }

        function Sb(a, d, f, g, h, j, k) {
            a = a | 0;
            d = d | 0;
            f = f | 0;
            g = g | 0;
            h = h | 0;
            j = j | 0;
            k = k | 0;
            var l = 0, m = 0, n = 0, o = 0, p = 0, q = 0, r = 0, s = 0, t = 0, u = 0, v = 0, w = 0, x = 0, y = 0, z = 0,
                A = 0, B = 0, C = 0, D = 0, E = 0, F = 0, G = 0, H = 0, I = 0, J = 0, K = 0, L = 0;
            L = i;
            i = i + 3440 | 0;
            t = L + 3424 | 0;
            G = L + 3408 | 0;
            H = L + 3240 | 0;
            u = L + 3224 | 0;
            E = L + 3328 | 0;
            s = L + 3248 | 0;
            F = L + 24 | 0;
            K = L + 16 | 0;
            J = L;
            gc(f, a, E, 2, 4, 4, k);
            rd(E, d, s, H, 4, G, 4, k);
            fc(f, s, F, k);
            pd(8, 4, 4, E, F, G, H, u, k);
            d = g;
            a = d + 80 | 0;
            do {
                b[d >> 1] = 0;
                d = d + 2 | 0
            } while ((d | 0) < (a | 0));
            b[J >> 1] = -1;
            b[K >> 1] = -1;
            C = J + 2 | 0;
            b[C >> 1] = -1;
            D = K + 2 | 0;
            b[D >> 1] = -1;
            E = J + 4 | 0;
            b[E >> 1] = -1;
            F = K + 4 | 0;
            b[F >> 1] = -1;
            H = J + 6 | 0;
            b[H >> 1] = -1;
            G = K + 6 | 0;
            b[G >> 1] = -1;
            q = 0;
            do {
                o = b[u + (q << 1) >> 1] | 0;
                d = o >>> 2;
                m = d & 65535;
                a = o & 3;
                n = (b[s + (o << 1) >> 1] | 0) > 0;
                o = g + (o << 1) | 0;
                r = n & 1 ^ 1;
                b[o >> 1] = (e[o >> 1] | 0) + (n ? 8191 : 57345);
                b[t + (q << 1) >> 1] = n ? 32767 : -32768;
                n = J + (a << 1) | 0;
                o = b[n >> 1] | 0;
                do if (o << 16 >> 16 >= 0) {
                    p = K + (a << 1) | 0;
                    l = (o << 16 >> 16 | 0) <= (d << 16 >> 16 | 0);
                    d = J + ((a | 4) << 1) | 0;
                    if ((r & 65535 | 0) == (e[p >> 1] & 1 | 0)) if (l) {
                        b[d >> 1] = m;
                        break
                    } else {
                        b[d >> 1] = o;
                        b[n >> 1] = m;
                        b[p >> 1] = r;
                        break
                    } else if (l) {
                        b[d >> 1] = o;
                        b[n >> 1] = m;
                        b[p >> 1] = r;
                        break
                    } else {
                        b[d >> 1] = m;
                        break
                    }
                } else {
                    b[n >> 1] = m;
                    b[K + (a << 1) >> 1] = r
                } while (0);
                q = q + 1 | 0
            } while ((q | 0) != 8);
            v = t + 2 | 0;
            w = t + 4 | 0;
            x = t + 6 | 0;
            y = t + 8 | 0;
            z = t + 10 | 0;
            A = t + 12 | 0;
            B = t + 14 | 0;
            t = b[t >> 1] | 0;
            q = 0;
            p = f + (0 - (b[u >> 1] | 0) << 1) | 0;
            o = f + (0 - (b[u + 2 >> 1] | 0) << 1) | 0;
            n = f + (0 - (b[u + 4 >> 1] | 0) << 1) | 0;
            m = f + (0 - (b[u + 6 >> 1] | 0) << 1) | 0;
            d = f + (0 - (b[u + 8 >> 1] | 0) << 1) | 0;
            a = f + (0 - (b[u + 10 >> 1] | 0) << 1) | 0;
            l = f + (0 - (b[u + 12 >> 1] | 0) << 1) | 0;
            f = f + (0 - (b[u + 14 >> 1] | 0) << 1) | 0;
            do {
                r = Z(b[p >> 1] | 0, t) | 0;
                p = p + 2 | 0;
                if ((r | 0) != 1073741824 ? (I = r << 1, !((r | 0) > 0 & (I | 0) < 0)) : 0) r = I; else {
                    c[k >> 2] = 1;
                    r = 2147483647
                }
                s = Z(b[v >> 1] | 0, b[o >> 1] | 0) | 0;
                o = o + 2 | 0;
                if ((s | 0) != 1073741824) {
                    g = (s << 1) + r | 0;
                    if ((s ^ r | 0) > 0 & (g ^ r | 0) < 0) {
                        c[k >> 2] = 1;
                        r = (r >>> 31) + 2147483647 | 0
                    } else r = g
                } else {
                    c[k >> 2] = 1;
                    r = 2147483647
                }
                s = Z(b[w >> 1] | 0, b[n >> 1] | 0) | 0;
                n = n + 2 | 0;
                if ((s | 0) != 1073741824) {
                    g = (s << 1) + r | 0;
                    if ((s ^ r | 0) > 0 & (g ^ r | 0) < 0) {
                        c[k >> 2] = 1;
                        g = (r >>> 31) + 2147483647 | 0
                    }
                } else {
                    c[k >> 2] = 1;
                    g = 2147483647
                }
                s = Z(b[x >> 1] | 0, b[m >> 1] | 0) | 0;
                m = m + 2 | 0;
                if ((s | 0) != 1073741824) {
                    r = (s << 1) + g | 0;
                    if ((s ^ g | 0) > 0 & (r ^ g | 0) < 0) {
                        c[k >> 2] = 1;
                        r = (g >>> 31) + 2147483647 | 0
                    }
                } else {
                    c[k >> 2] = 1;
                    r = 2147483647
                }
                s = Z(b[y >> 1] | 0, b[d >> 1] | 0) | 0;
                d = d + 2 | 0;
                if ((s | 0) != 1073741824) {
                    g = (s << 1) + r | 0;
                    if ((s ^ r | 0) > 0 & (g ^ r | 0) < 0) {
                        c[k >> 2] = 1;
                        g = (r >>> 31) + 2147483647 | 0
                    }
                } else {
                    c[k >> 2] = 1;
                    g = 2147483647
                }
                s = Z(b[z >> 1] | 0, b[a >> 1] | 0) | 0;
                a = a + 2 | 0;
                if ((s | 0) != 1073741824) {
                    r = (s << 1) + g | 0;
                    if ((s ^ g | 0) > 0 & (r ^ g | 0) < 0) {
                        c[k >> 2] = 1;
                        r = (g >>> 31) + 2147483647 | 0
                    }
                } else {
                    c[k >> 2] = 1;
                    r = 2147483647
                }
                s = Z(b[A >> 1] | 0, b[l >> 1] | 0) | 0;
                l = l + 2 | 0;
                if ((s | 0) != 1073741824) {
                    g = (s << 1) + r | 0;
                    if ((s ^ r | 0) > 0 & (g ^ r | 0) < 0) {
                        c[k >> 2] = 1;
                        g = (r >>> 31) + 2147483647 | 0
                    }
                } else {
                    c[k >> 2] = 1;
                    g = 2147483647
                }
                s = Z(b[B >> 1] | 0, b[f >> 1] | 0) | 0;
                f = f + 2 | 0;
                if ((s | 0) != 1073741824) {
                    r = (s << 1) + g | 0;
                    if ((s ^ g | 0) > 0 & (r ^ g | 0) < 0) {
                        c[k >> 2] = 1;
                        r = (g >>> 31) + 2147483647 | 0
                    }
                } else {
                    c[k >> 2] = 1;
                    r = 2147483647
                }
                b[h + (q << 1) >> 1] = Ce(r, k) | 0;
                q = q + 1 | 0
            } while ((q | 0) != 40);
            b[j >> 1] = b[K >> 1] | 0;
            b[j + 2 >> 1] = b[D >> 1] | 0;
            b[j + 4 >> 1] = b[F >> 1] | 0;
            b[j + 6 >> 1] = b[G >> 1] | 0;
            a = b[J >> 1] | 0;
            d = b[J + 8 >> 1] | 0;
            l = b[C >> 1] | 0;
            b[j + 8 >> 1] = d << 1 & 2 | a & 1 | l << 2 & 4 | (((d >> 1) * 327680 | 0) + (a >>> 1 << 16) + (Z(l >> 1, 1638400) | 0) | 0) >>> 13 & 65528;
            l = b[E >> 1] | 0;
            a = b[J + 12 >> 1] | 0;
            d = b[J + 10 >> 1] | 0;
            b[j + 10 >> 1] = a << 1 & 2 | l & 1 | d << 2 & 4 | (((a >> 1) * 327680 | 0) + (l >>> 1 << 16) + (Z(d >> 1, 1638400) | 0) | 0) >>> 13 & 65528;
            d = b[J + 14 >> 1] | 0;
            l = b[H >> 1] | 0;
            a = l << 16 >> 16 >>> 1;
            if (!(d & 2)) {
                h = a;
                k = d << 16 >> 16;
                K = k >> 1;
                K = K * 327680 | 0;
                h = h << 16;
                K = h + K | 0;
                K = K << 5;
                K = K >> 16;
                K = K | 12;
                K = K * 2622 | 0;
                K = K >>> 16;
                h = l & 65535;
                h = h & 1;
                k = k << 17;
                k = k & 131072;
                K = K << 18;
                k = K | k;
                k = k >>> 16;
                h = k | h;
                h = h & 65535;
                j = j + 12 | 0;
                b[j >> 1] = h;
                i = L;
                return
            }
            h = 4 - (a << 16 >> 16) | 0;
            k = d << 16 >> 16;
            K = k >> 1;
            K = K * 327680 | 0;
            h = h << 16;
            K = h + K | 0;
            K = K << 5;
            K = K >> 16;
            K = K | 12;
            K = K * 2622 | 0;
            K = K >>> 16;
            h = l & 65535;
            h = h & 1;
            k = k << 17;
            k = k & 131072;

            K = K << 18;
            k = K | k;
            k = k >>> 16;
            h = k | h;
            h = h & 65535;
            j = j + 12 | 0;
            b[j >> 1] = h;
            i = L;
            return
        }

        function Tb(a, d, e, f, g) {
            a = a | 0;
            d = d | 0;
            e = e | 0;
            f = f | 0;
            g = g | 0;
            var h = 0, i = 0, j = 0, k = 0, l = 0, m = 0, n = 0, o = 0, p = 0, q = 0, r = 0, s = 0, t = 0;
            r = e << 16 >> 16;
            h = 0 - r | 0;
            e = g + (h << 2) | 0;
            g = ((r - (f << 16 >> 16) | 0) >>> 2) + 1 & 65535;
            if (g << 16 >> 16 <= 0) return;
            r = d << 16 >> 16 >>> 1 & 65535;
            if (!(r << 16 >> 16)) {
                _abort();//fix cc 精简
            }
            q = a + (h << 1) | 0;
            while (1) {
                l = q + 4 | 0;
                n = b[l >> 1] | 0;
                j = b[q >> 1] | 0;
                m = n;
                k = r;
                o = a;
                p = q;
                q = q + 8 | 0;
                i = 0;
                h = 0;
                f = 0;
                d = 0;
                while (1) {
                    t = b[o >> 1] | 0;
                    s = (Z(j << 16 >> 16, t) | 0) + i | 0;
                    i = b[p + 2 >> 1] | 0;
                    h = (Z(i, t) | 0) + h | 0;
                    j = (Z(m << 16 >> 16, t) | 0) + f | 0;
                    f = b[p + 6 >> 1] | 0;
                    m = (Z(f, t) | 0) + d | 0;
                    d = b[o + 2 >> 1] | 0;
                    i = s + (Z(d, i) | 0) | 0;
                    h = h + (Z(n << 16 >> 16, d) | 0) | 0;
                    l = l + 4 | 0;
                    f = j + (Z(d, f) | 0) | 0;
                    j = b[l >> 1] | 0;
                    d = m + (Z(j << 16 >> 16, d) | 0) | 0;
                    k = k + -1 << 16 >> 16;
                    if (!(k << 16 >> 16)) break;
                    t = n;
                    m = j;
                    n = b[p + 8 >> 1] | 0;
                    o = o + 4 | 0;
                    p = p + 4 | 0;
                    j = t
                }
                c[e >> 2] = i << 1;
                c[e + 4 >> 2] = h << 1;
                c[e + 8 >> 2] = f << 1;
                c[e + 12 >> 2] = d << 1;
                if (g << 16 >> 16 <= 1) break; else {
                    e = e + 16 | 0;
                    g = g + -1 << 16 >> 16
                }
            }
            return
        }

        function Ub(a, d, f, g, h, j, k, l, m) {
            a = a | 0;
            d = d | 0;
            f = f | 0;
            g = g | 0;
            h = h | 0;
            j = j | 0;
            k = k | 0;
            l = l | 0;
            m = m | 0;
            var n = 0, o = 0, p = 0, q = 0, r = 0, s = 0, t = 0, u = 0, v = 0, w = 0, x = 0, y = 0;
            y = i;
            i = i + 16 | 0;
            w = y + 2 | 0;
            x = y;
            do if (h << 16 >> 16 > 0) {
                s = g << 16 >> 16;
                u = 0;
                p = 0;
                g = 0;
                o = 0;
                t = 0;
                while (1) {
                    n = b[a + (u << 1) >> 1] | 0;
                    q = n << 16 >> 16;
                    p = (Z(q, q) | 0) + p | 0;
                    q = b[d + (u << 1) >> 1] | 0;
                    g = (Z(q, q) | 0) + g | 0;
                    o = (Z(b[f + (u << 1) >> 1] | 0, q) | 0) + o | 0;
                    q = Z(q, s) | 0;
                    if ((q | 0) == 1073741824) {
                        c[m >> 2] = 1;
                        r = 2147483647
                    } else r = q << 1;
                    q = r << 1;
                    q = (Ge(n, Ce((q >> 1 | 0) == (r | 0) ? q : r >> 31 ^ 2147483647, m) | 0, m) | 0) << 16 >> 16;
                    q = Z(q, q) | 0;
                    if ((q | 0) != 1073741824) {
                        n = (q << 1) + t | 0;
                        if ((q ^ t | 0) > 0 & (n ^ t | 0) < 0) {//不可精简
                            c[m >> 2] = 1;
                            n = (t >>> 31) + 2147483647 | 0
                        }
                    } else {
                        c[m >> 2] = 1;
                        n = 2147483647
                    }
                    u = u + 1 | 0;
                    if ((u & 65535) << 16 >> 16 == h << 16 >> 16) {
                        t = n;
                        break
                    } else t = n
                }
                p = p << 1;
                g = g << 1;
                o = o << 1;
                if ((p | 0) >= 0) {
                    if ((p | 0) < 400) {
                        n = t;
                        v = 14;
                        break
                    }
                } else {
                    c[m >> 2] = 1;
                    p = 2147483647
                }
                r = pe(p) | 0;
                q = r << 16 >> 16;
                if (r << 16 >> 16 > 0) {
                    n = p << q;
                    if ((n >> q | 0) != (p | 0)) n = p >> 31 ^ 2147483647
                } else {//不可精简
                    n = 0 - q << 16;
                    if ((n | 0) < 2031616) n = p >> (n >> 16); else n = 0
                }
                b[j >> 1] = n >>> 16;
                p = g;
                s = o;
                n = t;
                g = 15 - (r & 65535) & 65535
            } else {
                g = 0;
                o = 0;
                n = 0;
                v = 14
            } while (0);
            if ((v | 0) == 14) {
                b[j >> 1] = 0;
                p = g;
                s = o;
                g = -15
            }
            b[k >> 1] = g;
            if ((p | 0) < 0) {
                c[m >> 2] = 1;
                p = 2147483647
            }
            q = pe(p) | 0;
            o = q << 16 >> 16;
            if (q << 16 >> 16 > 0) {
                g = p << o;
                if ((g >> o | 0) != (p | 0)) g = p >> 31 ^ 2147483647
            } else {
                g = 0 - o << 16;
                if ((g | 0) < 2031616) g = p >> (g >> 16); else g = 0
            }
            b[j + 2 >> 1] = g >>> 16;
            b[k + 2 >> 1] = 15 - (q & 65535);
            p = pe(s) | 0;
            o = p << 16 >> 16;
            if (p << 16 >> 16 > 0) {
                g = s << o;
                if ((g >> o | 0) != (s | 0)) g = s >> 31 ^ 2147483647
            } else {
                g = 0 - o << 16;
                if ((g | 0) < 2031616) g = s >> (g >> 16); else g = 0
            }
            b[j + 4 >> 1] = g >>> 16;
            b[k + 4 >> 1] = 2 - (p & 65535);
            p = pe(n) | 0;
            g = p << 16 >> 16;
            if (p << 16 >> 16 > 0) {
                o = n << g;
                if ((o >> g | 0) != (n | 0)) o = n >> 31 ^ 2147483647
            } else {
                g = 0 - g << 16;
                if ((g | 0) < 2031616) o = n >> (g >> 16); else o = 0
            }
            g = o >>> 16 & 65535;
            n = 15 - (p & 65535) & 65535;
            b[j + 6 >> 1] = g;
            b[k + 6 >> 1] = n;
            if ((o >> 16 | 0) <= 0) {
                m = 0;
                b[l >> 1] = m;
                i = y;
                return
            }
            o = b[j >> 1] | 0;
            if (!(o << 16 >> 16)) {
                m = 0;
                b[l >> 1] = m;
                i = y;
                return
            }
            g = Td(De(o, 1, m) | 0, g) | 0;
            g = (g & 65535) << 16;
            o = ((Ge(n, b[k >> 1] | 0, m) | 0) & 65535) + 3 | 0;
            n = o & 65535;
            o = o << 16 >> 16;
            if (n << 16 >> 16 > 0) n = n << 16 >> 16 < 31 ? g >> o : 0; else {
                k = 0 - o << 16 >> 16;
                n = g << k;
                n = (n >> k | 0) == (g | 0) ? n : g >> 31 ^ 2147483647
            }
            de(n, w, x, m);
            x = Ic((e[w >> 1] | 0) + 65509 & 65535, b[x >> 1] | 0, m) | 0;
            w = x << 13;
            m = Ce((w >> 13 | 0) == (x | 0) ? w : x >> 31 ^ 2147483647, m) | 0;
            b[l >> 1] = m;
            i = y;
            return
        }

        function Vb(a, d, f, g, h, j, k, l, m, n, o) {
            a = a | 0;
            d = d | 0;
            f = f | 0;
            g = g | 0;
            h = h | 0;
            j = j | 0;
            k = k | 0;
            l = l | 0;
            m = m | 0;
            n = n | 0;
            o = o | 0;
            var p = 0, q = 0, r = 0, s = 0, t = 0, u = 0, v = 0, w = 0, x = 0, y = 0;
            y = i;
            i = i + 80 | 0;
            v = y;
            b[k >> 1] = b[j >> 1] | 0;
            b[l >> 1] = b[j + 2 >> 1] | 0;
            r = b[j + 4 >> 1] | 0;
            if (r << 16 >> 16 == -32768) r = 32767; else r = 0 - (r & 65535) & 65535;
            b[k + 2 >> 1] = r;
            b[l + 2 >> 1] = (e[j + 6 >> 1] | 0) + 1;
            switch (a | 0) {
                case 0:
                case 5: {
                    u = 0;
                    q = 0;
                    p = 0;
                    t = 0;
                    break
                }
                default: {
                    u = 0;
                    q = 1;
                    p = 1;
                    t = 1
                }
            }
            while (1) {
                s = (b[h + (u << 1) >> 1] | 0) >>> 3;
                b[v + (u << 1) >> 1] = s;
                s = s << 16 >> 16;
                r = Z(s, s) | 0;
                if ((r | 0) != 1073741824) {
                    j = (r << 1) + q | 0;
                    if ((r ^ q | 0) > 0 & (j ^ q | 0) < 0) {
                        c[o >> 2] = 1;
                        q = (q >>> 31) + 2147483647 | 0
                    } else q = j
                } else {
                    c[o >> 2] = 1;
                    q = 2147483647
                }
                r = Z(b[d + (u << 1) >> 1] | 0, s) | 0;
                if ((r | 0) != 1073741824) {
                    j = (r << 1) + p | 0;
                    if ((r ^ p | 0) > 0 & (j ^ p | 0) < 0) {
                        c[o >> 2] = 1;
                        p = (p >>> 31) + 2147483647 | 0
                    } else p = j
                } else {
                    c[o >> 2] = 1;
                    p = 2147483647
                }
                r = Z(b[g + (u << 1) >> 1] | 0, s) | 0;
                if ((r | 0) != 1073741824) {
                    j = (r << 1) + t | 0;
                    if ((r ^ t | 0) > 0 & (j ^ t | 0) < 0) {
                        c[o >> 2] = 1;
                        j = (t >>> 31) + 2147483647 | 0
                    }
                } else {
                    c[o >> 2] = 1;
                    j = 2147483647
                }
                u = u + 1 | 0;
                if ((u | 0) == 40) {
                    g = j;
                    s = p;
                    break
                } else t = j
            }
            p = pe(q) | 0;
            j = p << 16 >> 16;
            if (p << 16 >> 16 > 0) {
                r = q << j;
                if ((r >> j | 0) != (q | 0)) r = q >> 31 ^ 2147483647
            } else {
                r = 0 - j << 16;
                if ((r | 0) < 2031616) r = q >> (r >> 16); else r = 0
            }
            h = k + 4 | 0;
            b[h >> 1] = r >>> 16;
            d = l + 4 | 0;
            b[d >> 1] = -3 - (p & 65535);
            q = pe(s) | 0;
            j = q << 16 >> 16;
            if (q << 16 >> 16 > 0) {
                r = s << j;
                if ((r >> j | 0) != (s | 0)) r = s >> 31 ^ 2147483647
            } else {
                r = 0 - j << 16;
                if ((r | 0) < 2031616) r = s >> (r >> 16); else r = 0
            }
            j = r >>> 16;
            b[k + 6 >> 1] = (j | 0) == 32768 ? 32767 : 0 - j & 65535;
            b[l + 6 >> 1] = 7 - (q & 65535);
            q = pe(g) | 0;
            j = q << 16 >> 16;
            if (q << 16 >> 16 > 0) {
                r = g << j;
                if ((r >> j | 0) != (g | 0)) r = g >> 31 ^ 2147483647
            } else {
                r = 0 - j << 16;
                if ((r | 0) < 2031616) r = g >> (r >> 16); else r = 0
            }
            b[k + 8 >> 1] = r >>> 16;
            b[l + 8 >> 1] = 7 - (q & 65535);
            switch (a | 0) {
                case 0:
                case 5: {
                    r = 0;
                    p = 0;
                    break
                }
                default: {
                    i = y;
                    return
                }
            }
            do {
                p = (Z(b[v + (r << 1) >> 1] | 0, b[f + (r << 1) >> 1] | 0) | 0) + p | 0;
                r = r + 1 | 0
            } while ((r | 0) != 40);
            j = p << 1;
            r = pe(j) | 0;
            q = r << 16 >> 16;
            if (r << 16 >> 16 > 0) {
                p = j << q;
                if ((p >> q | 0) == (j | 0)) {
                    w = p;
                    x = 40
                } else {
                    w = j >> 31 ^ 2147483647;
                    x = 40
                }
            } else {
                p = 0 - q << 16;
                if ((p | 0) < 2031616) {
                    w = j >> (p >> 16);
                    x = 40
                }
            }
            if ((x | 0) == 40 ? (w >> 16 | 0) >= 1 : 0) {
                o = De(w >>> 16 & 65535, 1, o) | 0;
                b[m >> 1] = Td(o, b[h >> 1] | 0) | 0;
                b[n >> 1] = 65528 - (r & 65535) - (e[d >> 1] | 0);
                i = y;
                return
            }
            b[m >> 1] = 0;
            b[n >> 1] = 0;
            i = y;
            return
        }

        function Wb(a, d, e, f) {
            a = a | 0;
            d = d | 0;
            e = e | 0;
            f = f | 0;
            var g = 0, h = 0, i = 0;
            h = 0;
            g = 0;
            do {
                i = b[a + (h << 1) >> 1] | 0;
                g = (Z(i, i) | 0) + g | 0;
                h = h + 1 | 0
            } while ((h | 0) != 40);
            if ((g | 0) < 0) {
                c[f >> 2] = 1;
                g = 2147483647
            }
            f = pe(g) | 0;
            a = f << 16 >> 16;
            if (f << 16 >> 16 > 0) {
                h = g << a;
                if ((h >> a | 0) == (g | 0)) g = h; else g = g >> 31 ^ 2147483647
            } else {
                a = 0 - a << 16;
                if ((a | 0) < 2031616) g = g >> (a >> 16); else g = 0
            }
            b[e >> 1] = g >>> 16;
            b[d >> 1] = 16 - (f & 65535);
            return
        }

        function Xb(a, d, e, f, g, h, j, k, l, m, n, o, p) {
            a = a | 0;
            d = d | 0;
            e = e | 0;
            f = f | 0;
            g = g | 0;
            h = h | 0;
            j = j | 0;
            k = k | 0;
            l = l | 0;
            m = m | 0;
            n = n | 0;
            o = o | 0;
            p = p | 0;
            var q = 0, r = 0, s = 0, t = 0;
            r = i;
            i = i + 16 | 0;
            q = r;
            if (m >>> 0 < 2) {
                j = Nb(n, a, d, e, f, j, k, q, c[o + 76 >> 2] | 0, p) | 0;
                p = c[l >> 2] | 0;
                b[p >> 1] = j;
                j = b[q >> 1] | 0;
                c[l >> 2] = p + 4;
                b[p + 2 >> 1] = j;
                i = r;
                return
            }
            switch (m | 0) {
                case 2: {
                    j = Mb(a, d, e, f, j, k, q, p) | 0;
                    p = c[l >> 2] | 0;
                    b[p >> 1] = j;
                    j = b[q >> 1] | 0;
                    c[l >> 2] = p + 4;
                    b[p + 2 >> 1] = j;
                    i = r;
                    return
                }
                case 3: {
                    j = Qb(a, d, e, f, j, k, q, p) | 0;
                    p = c[l >> 2] | 0;
                    b[p >> 1] = j;
                    j = b[q >> 1] | 0;
                    c[l >> 2] = p + 4;
                    b[p + 2 >> 1] = j;
                    i = r;
                    return
                }
                default: {
                    if ((m & -2 | 0) == 4) {
                        j = Rb(a, d, e, f, j, k, q, c[o + 36 >> 2] | 0, p) | 0;
                        p = c[l >> 2] | 0;
                        b[p >> 1] = j;
                        j = b[q >> 1] | 0;
                        c[l >> 2] = p + 4;
                        b[p + 2 >> 1] = j;
                        i = r;
                        return
                    }
                    if ((m | 0) != 6) {
                        n = g << 16 >> 16;
                        n = (n << 17 >> 17 | 0) == (n | 0) ? n << 1 : n >>> 15 ^ 32767;
                        g = e << 16 >> 16 < 40;
                        if (!g) {
                            Lb(a, h, d, j, k, c[l >> 2] | 0, c[o + 36 >> 2] | 0, p);
                            c[l >> 2] = (c[l >> 2] | 0) + 20;
                            i = r;
                            return
                        }
                        q = e << 16 >> 16;
                        m = n << 16 >> 16;
                        f = q;
                        do {
                            t = (Z(b[d + (f - q << 1) >> 1] | 0, m) | 0) >>> 15 & 65535;
                            s = d + (f << 1) | 0;
                            b[s >> 1] = Rd(b[s >> 1] | 0, t, p) | 0;
                            f = f + 1 | 0
                        } while ((f & 65535) << 16 >> 16 != 40);
                        Lb(a, h, d, j, k, c[l >> 2] | 0, c[o + 36 >> 2] | 0, p);
                        c[l >> 2] = (c[l >> 2] | 0) + 20;
                        if (!g) {
                            i = r;
                            return
                        }
                        g = e << 16 >> 16;
                        m = n << 16 >> 16;
                        q = g;
                        do {
                            f = (Z(b[j + (q - g << 1) >> 1] | 0, m) | 0) >> 15;
                            if ((f | 0) > 32767) {
                                c[p >> 2] = 1;
                                f = 32767
                            }
                            t = j + (q << 1) | 0;
                            b[t >> 1] = Rd(b[t >> 1] | 0, f & 65535, p) | 0;
                            q = q + 1 | 0
                        } while ((q & 65535) << 16 >> 16 != 40);
                        i = r;
                        return
                    }
                    o = f << 16 >> 16;
                    o = (o << 17 >> 17 | 0) == (o | 0) ? o << 1 : o >>> 15 ^ 32767;
                    n = e << 16 >> 16 < 40;
                    if (!n) {
                        Sb(a, h, d, j, k, c[l >> 2] | 0, p);
                        c[l >> 2] = (c[l >> 2] | 0) + 14;
                        i = r;
                        return
                    }
                    q = e << 16 >> 16;
                    m = o << 16 >> 16;
                    f = q;
                    do {
                        g = (Z(b[d + (f - q << 1) >> 1] | 0, m) | 0) >> 15;
                        if ((g | 0) > 32767) {
                            c[p >> 2] = 1;
                            g = 32767
                        }
                        t = d + (f << 1) | 0;
                        b[t >> 1] = Rd(b[t >> 1] | 0, g & 65535, p) | 0;
                        f = f + 1 | 0
                    } while ((f & 65535) << 16 >> 16 != 40);
                    Sb(a, h, d, j, k, c[l >> 2] | 0, p);
                    c[l >> 2] = (c[l >> 2] | 0) + 14;
                    if (!n) {
                        i = r;
                        return
                    }
                    g = e << 16 >> 16;
                    m = o << 16 >> 16;
                    q = g;
                    do {
                        f = (Z(b[j + (q - g << 1) >> 1] | 0, m) | 0) >> 15;
                        if ((f | 0) > 32767) {
                            c[p >> 2] = 1;
                            f = 32767
                        }
                        t = j + (q << 1) | 0;
                        b[t >> 1] = Rd(b[t >> 1] | 0, f & 65535, p) | 0;
                        q = q + 1 | 0
                    } while ((q & 65535) << 16 >> 16 != 40);
                    i = r;
                    return
                }
            }
        }

        function Yb(a) {
            a = a | 0;
            var b = 0;
            if (!a) {
                a = -1;
                return a | 0
            }
            c[a >> 2] = 0;
            b = Je(4) | 0;
            if (!b) {
                a = -1;
                return a | 0
            }
            if (!((Uc(b) | 0) << 16 >> 16)) {
                Vc(c[b >> 2] | 0) | 0;
                c[a >> 2] = b;
                a = 0;
                return a | 0
            } else {
                Wc(b);
                Ke(b);
                a = -1;
                return a | 0
            }
            return 0
        }

        function Zb(a) {
            a = a | 0;
            var b = 0;
            if (!a) return;
            b = c[a >> 2] | 0;
            if (!b) return;
            Wc(b);
            Ke(c[a >> 2] | 0);
            c[a >> 2] = 0;
            return
        }

        function _b(a) {
            a = a | 0;
            if (!a) {
                a = -1;
                return a | 0
            }
            Vc(c[a >> 2] | 0) | 0;
            a = 0;
            return a | 0
        }

        function $b(a, d, f, g, h, j, k, l, m, n, o, p, q, r, s, t, u, v, w, x) {
            a = a | 0;
            d = d | 0;
            f = f | 0;
            g = g | 0;
            h = h | 0;
            j = j | 0;
            k = k | 0;
            l = l | 0;
            m = m | 0;
            n = n | 0;
            o = o | 0;
            p = p | 0;
            q = q | 0;
            r = r | 0;
            s = s | 0;
            t = t | 0;
            u = u | 0;
            v = v | 0;
            w = w | 0;
            x = x | 0;
            var y = 0, z = 0, A = 0, B = 0;
            z = i;
            i = i + 16 | 0;
            B = z + 2 | 0;
            A = z;
            b[q >> 1] = Xc(c[a >> 2] | 0, f, h, k, m, j, 40, g, r, A, B, x) | 0;
            a = b[B >> 1] | 0;
            g = c[u >> 2] | 0;
            c[u >> 2] = g + 2;
            b[g >> 1] = a;
            se(k, b[q >> 1] | 0, b[r >> 1] | 0, 40, b[A >> 1] | 0, x);
            ec(k, j, p, 40);
            b[s >> 1] = Dc(f, m, p, t, 40, x) | 0;
            b[v >> 1] = 32767;
            if (n << 16 >> 16 != 0 ? (y = b[s >> 1] | 0, y << 16 >> 16 > 15565) : 0) y = Ed(d, y, x) | 0; else y = 0;
            if (f >>> 0 < 2) {
                B = b[s >> 1] | 0;
                b[s >> 1] = B << 16 >> 16 > 13926 ? 13926 : B;
                if (y << 16 >> 16) b[v >> 1] = 15565
            } else {
                if (y << 16 >> 16) {
                    b[v >> 1] = 15565;
                    b[s >> 1] = 15565
                }
                if ((f | 0) == 7) {
                    A = nd(7, b[v >> 1] | 0, s, 0, 0, w, x) | 0;
                    B = c[u >> 2] | 0;
                    c[u >> 2] = B + 2;
                    b[B >> 1] = A
                }
            }
            q = b[s >> 1] | 0;
            y = 0;
            while (1) {
                A = Z(b[p >> 1] | 0, q) | 0;
                b[o >> 1] = (e[m >> 1] | 0) - (A >>> 14);
                A = (Z(b[k >> 1] | 0, q) | 0) >>> 14;
                B = l + (y << 1) | 0;
                b[B >> 1] = (e[B >> 1] | 0) - A;
                y = y + 1 | 0;
                if ((y | 0) == 40) break; else {
                    k = k + 2 | 0;
                    m = m + 2 | 0;
                    o = o + 2 | 0;
                    p = p + 2 | 0
                }
            }
            i = z;
            return
        }

        function ac(a, b) {
            a = a | 0;
            b = b | 0;
            var d = 0, e = 0, f = 0, g = 0;
            g = i;
            i = i + 16 | 0;
            f = g;
            if (!a) {
                a = -1;
                i = g;
                return a | 0
            }
            c[a >> 2] = 0;
            d = Je(2532) | 0;
            c[f >> 2] = d;
            if (!d) {
                a = -1;
                i = g;
                return a | 0
            }
            Yd(d + 2392 | 0);
            c[d + 2188 >> 2] = 0;
            c[(c[f >> 2] | 0) + 2192 >> 2] = 0;
            c[(c[f >> 2] | 0) + 2196 >> 2] = 0;
            c[(c[f >> 2] | 0) + 2200 >> 2] = 0;
            c[(c[f >> 2] | 0) + 2204 >> 2] = 0;
            c[(c[f >> 2] | 0) + 2208 >> 2] = 0;
            c[(c[f >> 2] | 0) + 2212 >> 2] = 0;
            c[(c[f >> 2] | 0) + 2220 >> 2] = 0;
            e = c[f >> 2] | 0;
            c[e + 2216 >> 2] = b;
            c[e + 2528 >> 2] = 0;
            d = e;
            if ((((((((Yb(e + 2196 | 0) | 0) << 16 >> 16 == 0 ? (ie(e + 2192 | 0) | 0) << 16 >> 16 == 0 : 0) ? (yc(e + 2200 | 0) | 0) << 16 >> 16 == 0 : 0) ? (_c(e + 2204 | 0) | 0) << 16 >> 16 == 0 : 0) ? (Ad(e + 2208 | 0) | 0) << 16 >> 16 == 0 : 0) ? (Gd(e + 2212 | 0) | 0) << 16 >> 16 == 0 : 0) ? (jc(e + 2220 | 0, c[e + 2432 >> 2] | 0) | 0) << 16 >> 16 == 0 : 0) ? (Pc(e + 2188 | 0) | 0) << 16 >> 16 == 0 : 0) {
                cc(e) | 0;
                c[a >> 2] = d;
                a = 0;
                i = g;
                return a | 0
            }
            bc(f);
            a = -1;
            i = g;
            return a | 0
        }

        function bc(a) {
            a = a | 0;
            var b = 0;
            if (!a) return;
            b = c[a >> 2] | 0;
            if (!b) return;
            Qc(b + 2188 | 0);
            ke((c[a >> 2] | 0) + 2192 | 0);
            zc((c[a >> 2] | 0) + 2200 | 0);
            Zb((c[a >> 2] | 0) + 2196 | 0);
            ad((c[a >> 2] | 0) + 2204 | 0);
            Cd((c[a >> 2] | 0) + 2208 | 0);
            Id((c[a >> 2] | 0) + 2212 | 0);
            lc((c[a >> 2] | 0) + 2220 | 0);
            Ke(c[a >> 2] | 0);
            c[a >> 2] = 0;
            return
        }

        function cc(a) {
            a = a | 0;
            var d = 0, e = 0, f = 0, g = 0;
            if (!a) {
                g = -1;
                return g | 0
            }
            c[a + 652 >> 2] = a + 320;
            c[a + 640 >> 2] = a + 240;
            c[a + 644 >> 2] = a + 160;
            c[a + 648 >> 2] = a + 80;
            c[a + 1264 >> 2] = a + 942;
            c[a + 1912 >> 2] = a + 1590;
            f = a + 1938 | 0;
            c[a + 2020 >> 2] = f;
            c[a + 2384 >> 2] = a + 2304;
            d = a + 2028 | 0;
            c[a + 2024 >> 2] = a + 2108;
            c[a + 2528 >> 2] = 0;
            Qe(a | 0, 0, 640) | 0;
            Qe(a + 1282 | 0, 0, 308) | 0;
            Qe(a + 656 | 0, 0, 286) | 0;
            e = a + 2224 | 0;
            g = f + 80 | 0;
            do {
                b[f >> 1] = 0;
                f = f + 2 | 0
            } while ((f | 0) < (g | 0));
            f = d;
            g = f + 80 | 0;
            do {
                b[f >> 1] = 0;
                f = f + 2 | 0
            } while ((f | 0) < (g | 0));
            d = a + 1268 | 0;
            f = e;
            g = f + 80 | 0;
            do {
                b[f >> 1] = 0;
                f = f + 2 | 0
            } while ((f | 0) < (g | 0));
            b[d >> 1] = 40;
            b[a + 1270 >> 1] = 40;
            b[a + 1272 >> 1] = 40;
            b[a + 1274 >> 1] = 40;
            b[a + 1276 >> 1] = 40;
            Rc(c[a + 2188 >> 2] | 0) | 0;
            je(c[a + 2192 >> 2] | 0) | 0;
            _b(c[a + 2196 >> 2] | 0) | 0;
            Ac(c[a + 2200 >> 2] | 0) | 0;
            $c(c[a + 2204 >> 2] | 0) | 0;
            Bd(c[a + 2208 >> 2] | 0) | 0;
            Hd(c[a + 2212 >> 2] | 0) | 0;
            kc(c[a + 2220 >> 2] | 0, c[a + 2432 >> 2] | 0) | 0;
            b[a + 2388 >> 1] = 0;
            g = 0;
            return g | 0
        }

        function dc(a, d, e, f, g, h) {
            a = a | 0;
            d = d | 0;
            e = e | 0;
            f = f | 0;
            g = g | 0;
            h = h | 0;
            var j = 0, k = 0, l = 0, m = 0, n = 0, o = 0, p = 0, q = 0, r = 0, s = 0, t = 0, u = 0, v = 0, w = 0, x = 0,
                y = 0, z = 0, A = 0, B = 0, C = 0, D = 0, E = 0, F = 0, G = 0, H = 0, I = 0, J = 0, K = 0, L = 0, M = 0,
                N = 0, O = 0, P = 0, Q = 0, R = 0, S = 0, T = 0, U = 0, V = 0, W = 0, X = 0, Y = 0, Z = 0, _ = 0, $ = 0,
                aa = 0, ba = 0, ca = 0, da = 0, ea = 0, fa = 0, ga = 0, ha = 0, ia = 0, ja = 0, ka = 0, la = 0, ma = 0,
                na = 0, oa = 0, pa = 0, qa = 0;
            qa = i;
            i = i + 1184 | 0;
            T = qa;
            n = qa + 1096 | 0;
            o = qa + 1008 | 0;
            l = qa + 904 | 0;
            ka = qa + 928 | 0;
            la = qa + 824 | 0;
            X = qa + 744 | 0;
            na = qa + 664 | 0;
            oa = qa + 584 | 0;
            Z = qa + 328 | 0;
            ha = qa + 504 | 0;
            ia = qa + 424 | 0;
            ma = qa + 344 | 0;
            pa = qa + 248 | 0;
            Y = qa + 168 | 0;
            da = qa + 88 | 0;
            fa = qa + 68 | 0;
            ga = qa + 48 | 0;
            ea = qa + 28 | 0;
            ja = qa + 24 | 0;
            ba = qa + 22 | 0;
            $ = qa + 20 | 0;
            W = qa + 16 | 0;
            U = qa + 12 | 0;
            V = qa + 10 | 0;
            aa = qa + 8 | 0;
            _ = qa + 6 | 0;
            ca = qa + 4 | 0;
            c[T >> 2] = f;
            S = a + 2528 | 0;
            j = a + 652 | 0;
            Oe(c[j >> 2] | 0, e | 0, 320) | 0;
            c[g >> 2] = d;
            m = a + 2216 | 0;
            if (!(c[m >> 2] | 0)) {
                e = a + 2220 | 0;
                f = 0
            } else {
                _abort();//fix cc 精简
				
				
				
            }
            R = a + 2392 | 0;
            Sc(c[a + 2188 >> 2] | 0, d, c[a + 644 >> 2] | 0, c[a + 648 >> 2] | 0, n, R, S);
            k = a + 2192 | 0;
            le(c[k >> 2] | 0, d, c[g >> 2] | 0, n, o, l, T, S);
            nc(c[e >> 2] | 0, l, c[j >> 2] | 0, S);
            if ((c[g >> 2] | 0) == 8) {
                _abort();//fix cc 精简
            } else Q = Dd(c[a + 2208 >> 2] | 0, c[k >> 2] | 0, S) | 0;
            N = a + 640 | 0;
            k = a + 2264 | 0;
            j = a + 1264 | 0;
            e = a + 2204 | 0;
            f = a + 2212 | 0;
            O = a + 1268 | 0;
            P = a + 1278 | 0;
            cd(d, 2842, 2862, 2882, n, 0, c[N >> 2] | 0, k, c[j >> 2] | 0, S);
            if (d >>> 0 > 1) {
                Tc(c[e >> 2] | 0, c[f >> 2] | 0, d, c[j >> 2] | 0, W, O, P, 0, c[m >> 2] | 0, S);
                cd(d, 2842, 2862, 2882, n, 80, c[N >> 2] | 0, k, c[j >> 2] | 0, S);
                Tc(c[e >> 2] | 0, c[f >> 2] | 0, d, (c[j >> 2] | 0) + 160 | 0, W + 2 | 0, O, P, 1, c[m >> 2] | 0, S)
            } else {
                cd(d, 2842, 2862, 2882, n, 80, c[N >> 2] | 0, k, c[j >> 2] | 0, S);
                Tc(c[e >> 2] | 0, c[f >> 2] | 0, d, c[j >> 2] | 0, W, O, P, 1, c[m >> 2] | 0, S);
                b[W + 2 >> 1] = b[W >> 1] | 0
            }
            if (c[m >> 2] | 0) _abort();//fix cc 精简
            if ((c[g >> 2] | 0) == 8) {
                _abort();//fix cc 精简
            }
            z = a + 2224 | 0;
            A = a + 2244 | 0;
            B = a + 2284 | 0;
            C = a + 2388 | 0;
            D = a + 2020 | 0;
            E = a + 1916 | 0;
            F = a + 1912 | 0;
            G = a + 2024 | 0;
            H = a + 2384 | 0;
            I = a + 2196 | 0;
            J = a + 2208 | 0;
            K = a + 2464 | 0;
            L = a + 2200 | 0;
            M = a + 2224 | 0;
            w = a + 2244 | 0;
            x = a + 1270 | 0;
            y = a + 1280 | 0;
            v = 0;
            m = 0;
            l = 0;
            s = 0;
            t = 0;
            k = 0;
            u = -1;
            while (1) {
                p = u;
                u = u + 1 << 16 >> 16;
                s = 1 - (s << 16 >> 16) | 0;
                f = s & 65535;
                r = (s & 65535 | 0) != 0;
                e = c[g >> 2] | 0;
                j = (e | 0) == 0;
                do if (r) if (j) {
                    j = fa;
                    e = z;
                    q = j + 20 | 0;
                    do {
                        b[j >> 1] = b[e >> 1] | 0;
                        j = j + 2 | 0;
                        e = e + 2 | 0
                    } while ((j | 0) < (q | 0));
                    j = ga;
                    e = A;
                    q = j + 20 | 0;
                    do {
                        b[j >> 1] = b[e >> 1] | 0;
                        j = j + 2 | 0;
                        e = e + 2 | 0
                    } while ((j | 0) < (q | 0));
                    j = ea;
                    e = B;
                    q = j + 20 | 0;
                    do {
                        b[j >> 1] = b[e >> 1] | 0;
                        j = j + 2 | 0;
                        e = e + 2 | 0
                    } while ((j | 0) < (q | 0));
                    b[ja >> 1] = b[C >> 1] | 0;
                    d = (c[N >> 2] | 0) + (v << 1) | 0;
                    j = 20;
                    break
                } else {
                    d = (c[N >> 2] | 0) + (v << 1) | 0;
                    j = 19;
                    break
                } else {
                    d = (c[N >> 2] | 0) + (v << 1) | 0;
                    if (j) j = 20; else j = 19
                } while (0);
                if ((j | 0) == 19) yd(e, 2842, 2862, 2882, n, o, d, B, w, c[D >> 2] | 0, E, (c[F >> 2] | 0) + (v << 1) | 0, c[G >> 2] | 0, ka, ha, c[H >> 2] | 0); else if ((j | 0) == 20 ? (0, yd(0, 2842, 2862, 2882, n, o, d, B, ga, c[D >> 2] | 0, E, (c[F >> 2] | 0) + (v << 1) | 0, c[G >> 2] | 0, ka, ha, c[H >> 2] | 0), r) : 0) {
                    j = da;
                    e = c[G >> 2] | 0;
                    q = j + 80 | 0;
                    do {
                        b[j >> 1] = b[e >> 1] | 0;
                        j = j + 2 | 0;
                        e = e + 2 | 0
                    } while ((j | 0) < (q | 0))
                }
                j = ia;
                e = ha;
                q = j + 80 | 0;
                do {
                    b[j >> 1] = b[e >> 1] | 0;
                    j = j + 2 | 0;
                    e = e + 2 | 0
                } while ((j | 0) < (q | 0));
                $b(c[I >> 2] | 0, c[J >> 2] | 0, c[g >> 2] | 0, t, W, c[G >> 2] | 0, (c[F >> 2] | 0) + (v << 1) | 0, ia, ka, Q, la, na, U, V, aa, Z, T, ca, c[K >> 2] | 0, S);
                switch (p << 16 >> 16) {
                    case -1: {
                        if ((b[P >> 1] | 0) > 0) b[x >> 1] = b[U >> 1] | 0;
                        break
                    }
                    case 2: {
                        if ((b[y >> 1] | 0) > 0) b[O >> 1] = b[U >> 1] | 0;
                        break
                    }
                    default: {
                    }
                }
                Xb(la, c[G >> 2] | 0, b[U >> 1] | 0, b[C >> 1] | 0, b[aa >> 1] | 0, ia, X, oa, T, c[g >> 2] | 0, u, R, S);
                Bc(c[L >> 2] | 0, c[g >> 2] | 0, ha, (c[F >> 2] | 0) + (v << 1) | 0, X, ka, la, na, oa, Z, f, b[ca >> 1] | 0, ba, $, aa, _, T, R, S);
                Fd(c[J >> 2] | 0, b[aa >> 1] | 0, S);
                d = c[g >> 2] | 0;
                do if (!d) if (r) {
                    j = ma;
                    e = ka;
                    q = j + 80 | 0;
                    do {
                        b[j >> 1] = b[e >> 1] | 0;
                        j = j + 2 | 0;
                        e = e + 2 | 0
                    } while ((j | 0) < (q | 0));
                    j = pa;
                    e = oa;
                    q = j + 80 | 0;
                    do {
                        b[j >> 1] = b[e >> 1] | 0;
                        j = j + 2 | 0;
                        e = e + 2 | 0
                    } while ((j | 0) < (q | 0));
                    j = Y;
                    e = X;
                    q = j + 80 | 0;
                    do {
                        b[j >> 1] = b[e >> 1] | 0;
                        j = j + 2 | 0;
                        e = e + 2 | 0
                    } while ((j | 0) < (q | 0));
                    l = b[U >> 1] | 0;
                    m = b[V >> 1] | 0;
                    zd(c[N >> 2] | 0, 0, t, b[aa >> 1] | 0, b[_ >> 1] | 0, o, h, ka, X, na, oa, fa, B, ga, c[F >> 2] | 0, C, S);
                    b[C >> 1] = b[ja >> 1] | 0;
                    k = t;
                    break
                } else {
                    j = B;
                    e = ea;
                    q = j + 20 | 0;
                    do {
                        b[j >> 1] = b[e >> 1] | 0;
                        j = j + 2 | 0;
                        e = e + 2 | 0
                    } while ((j | 0) < (q | 0));
                    r = k << 16 >> 16;
                    se((c[F >> 2] | 0) + (r << 1) | 0, l, m, 40, 1, S);
                    ec((c[F >> 2] | 0) + (r << 1) | 0, da, na, 40);
                    zd(c[N >> 2] | 0, c[g >> 2] | 0, k, b[ba >> 1] | 0, b[$ >> 1] | 0, o + -22 | 0, h, ma, Y, na, pa, M, B, w, c[F >> 2] | 0, ja, S);
                    yd(c[g >> 2] | 0, 2842, 2862, 2882, n, o, (c[N >> 2] | 0) + (v << 1) | 0, B, w, c[D >> 2] | 0, E, (c[F >> 2] | 0) + (v << 1) | 0, c[G >> 2] | 0, ka, ha, c[H >> 2] | 0);
                    se((c[F >> 2] | 0) + (v << 1) | 0, b[U >> 1] | 0, b[V >> 1] | 0, 40, 1, S);
                    ec((c[F >> 2] | 0) + (v << 1) | 0, c[G >> 2] | 0, na, 40);
                    zd(c[N >> 2] | 0, c[g >> 2] | 0, t, b[aa >> 1] | 0, b[_ >> 1] | 0, o, h, ka, X, na, oa, M, B, w, c[F >> 2] | 0, C, S);
                    break
                } else zd(c[N >> 2] | 0, d, t, b[aa >> 1] | 0, b[_ >> 1] | 0, o, h, ka, X, na, oa, M, B, w, c[F >> 2] | 0, C, S); while (0);
                d = v + 40 | 0;
                t = d & 65535;
                if (t << 16 >> 16 >= 160) break; else {
                    v = d << 16 >> 16;
                    n = n + 22 | 0;
                    o = o + 22 | 0
                }
            }
            Oe(a + 1282 | 0, a + 1602 | 0, 308) | 0;
            oa = a + 656 | 0;
            pa = a + 976 | 0;
            Oe(oa | 0, pa | 0, 286) | 0;
            pa = a + 320 | 0;
            Oe(a | 0, pa | 0, 320) | 0;
            i = qa;
            return 0
        }

        function ec(a, c, d, e) {
            a = a | 0;
            c = c | 0;
            d = d | 0;
            e = e | 0;
            var f = 0, g = 0, h = 0, i = 0, j = 0, k = 0, l = 0, m = 0, n = 0, o = 0, p = 0, q = 0;
            o = e << 16 >> 16;
            if (e << 16 >> 16 > 1) n = 1; else return;
            while (1) {
                f = b[a >> 1] | 0;
                i = c + (n + -1 << 1) | 0;
                e = Z(b[c + (n << 1) >> 1] | 0, f) | 0;
                k = b[i >> 1] | 0;
                f = Z(k << 16 >> 16, f) | 0;
                h = (n + 131071 | 0) >>> 1;
                j = h & 65535;
                g = b[a + 2 >> 1] | 0;
                if (!(j << 16 >> 16)) {
                    c = i;
                    h = k
                } else {
                    l = (h << 1) + 131070 & 131070;
                    m = n - l | 0;
                    h = a;
                    do {
                        q = (Z(k << 16 >> 16, g) | 0) + e | 0;
                        p = h;
                        h = h + 4 | 0;
                        e = b[i + -2 >> 1] | 0;
                        g = (Z(e, g) | 0) + f | 0;
                        f = b[h >> 1] | 0;
                        i = i + -4 | 0;
                        e = q + (Z(f, e) | 0) | 0;
                        k = b[i >> 1] | 0;
                        f = g + (Z(k << 16 >> 16, f) | 0) | 0;
                        j = j + -1 << 16 >> 16;
                        g = b[p + 6 >> 1] | 0
                    } while (j << 16 >> 16 != 0);
                    h = c + (m + -3 << 1) | 0;
                    a = a + (l + 2 << 1) | 0;
                    c = h;
                    h = b[h >> 1] | 0
                }
                e = (Z(h << 16 >> 16, g) | 0) + e | 0;
                b[d >> 1] = f >>> 12;
                b[d + 2 >> 1] = e >>> 12;
                e = (n << 16) + 131072 >> 16;
                if ((e | 0) < (o | 0)) {
                    d = d + 4 | 0;
                    a = a + (1 - n << 1) | 0;
                    n = e
                } else break
            }
            return
        }

        function fc(a, c, d, e) {
            a = a | 0;
            c = c | 0;
            d = d | 0;
            e = e | 0;
            var f = 0, g = 0, h = 0, j = 0, k = 0, l = 0, m = 0, n = 0, o = 0, p = 0, q = 0, r = 0, s = 0, t = 0, u = 0,
                v = 0, w = 0, x = 0, y = 0, z = 0, A = 0, B = 0;
            z = i;
            i = i + 80 | 0;
            y = z;
            h = 20;
            g = a;
            f = 1;
            while (1) {
                x = b[g >> 1] | 0;
                x = (Z(x, x) | 0) + f | 0;
                f = b[g + 2 >> 1] | 0;
                f = x + (Z(f, f) | 0) | 0;
                h = h + -1 << 16 >> 16;
                if (!(h << 16 >> 16)) break; else g = g + 4 | 0
            }
            f = f << 1;
            if ((f | 0) < 0) {
                g = 20;
                f = a;
                e = y;
                while (1) {
                    b[e >> 1] = (b[f >> 1] | 0) >>> 1;
                    b[e + 2 >> 1] = (b[f + 2 >> 1] | 0) >>> 1;
                    g = g + -1 << 16 >> 16;
                    if (!(g << 16 >> 16)) {
                        x = y;
                        break
                    } else {
                        f = f + 4 | 0;
                        e = e + 4 | 0
                    }
                }
            } else {
                f = ce(f >> 1, e) | 0;
                if ((f | 0) < 16777215) f = ((f >> 9) * 32440 | 0) >>> 15 << 16 >> 16; else f = 32440;
                h = 20;
                g = a;
                e = y;
                while (1) {
                    b[e >> 1] = ((Z(b[g >> 1] | 0, f) | 0) + 32 | 0) >>> 6;
                    b[e + 2 >> 1] = ((Z(b[g + 2 >> 1] | 0, f) | 0) + 32 | 0) >>> 6;
                    h = h + -1 << 16 >> 16;
                    if (!(h << 16 >> 16)) {
                        x = y;
                        break
                    } else {
                        g = g + 4 | 0;
                        e = e + 4 | 0
                    }
                }
            }
            h = 20;
            g = x;
            e = d + 3198 | 0;
            f = 0;
            while (1) {
                w = b[g >> 1] | 0;
                w = (Z(w, w) | 0) + f | 0;
                b[e >> 1] = (w + 16384 | 0) >>> 15;
                v = b[g + 2 >> 1] | 0;
                f = (Z(v, v) | 0) + w | 0;
                b[e + -82 >> 1] = (f + 16384 | 0) >>> 15;
                h = h + -1 << 16 >> 16;
                if (!(h << 16 >> 16)) break; else {
                    g = g + 4 | 0;
                    e = e + -164 | 0
                }
            }
            w = c + 78 | 0;
            v = 1;
            while (1) {
                f = 39 - v | 0;
                a = d + 3120 + (f << 1) | 0;
                e = d + (f * 80 | 0) + 78 | 0;
                f = c + (f << 1) | 0;
                k = y + (v << 1) | 0;
                g = 65575 - v | 0;
                j = g & 65535;
                h = b[x >> 1] | 0;
                if (!(j << 16 >> 16)) {
                    j = w;
                    g = 0
                } else {
                    r = g + 65535 & 65535;
                    t = r * 41 | 0;
                    u = (Z(v, -40) | 0) - t | 0;
                    s = 0 - v | 0;
                    t = s - t | 0;
                    s = s - r | 0;
                    q = v + r | 0;
                    p = b[k >> 1] | 0;
                    n = x;
                    o = w;
                    l = d + ((38 - v | 0) * 80 | 0) + 78 | 0;
                    g = 0;
                    m = 0;
                    while (1) {
                        k = k + 2 | 0;
                        g = (Z(p << 16 >> 16, h) | 0) + g | 0;
                        n = n + 2 | 0;
                        p = b[k >> 1] | 0;
                        m = (Z(p << 16 >> 16, h) | 0) + m | 0;
                        B = f;
                        f = f + -2 | 0;
                        h = b[f >> 1] | 0;
                        A = b[o >> 1] << 1;
                        B = (Z((Z(A, b[B >> 1] | 0) | 0) >> 16, (g << 1) + 32768 >> 16) | 0) >>> 15 & 65535;
                        b[e >> 1] = B;
                        b[a >> 1] = B;
                        h = (Z((Z(A, h) | 0) >> 16, (m << 1) + 32768 >> 16) | 0) >>> 15 & 65535;
                        b[a + -2 >> 1] = h;
                        b[l >> 1] = h;
                        j = j + -1 << 16 >> 16;
                        h = b[n >> 1] | 0;
                        if (!(j << 16 >> 16)) break; else {
                            o = o + -2 | 0;
                            a = a + -82 | 0;
                            e = e + -82 | 0;
                            l = l + -82 | 0
                        }
                    }
                    k = y + (q + 1 << 1) | 0;
                    j = c + (38 - r << 1) | 0;
                    f = c + (s + 38 << 1) | 0;
                    a = d + 3040 + (t + 38 << 1) | 0;
                    e = d + 3040 + (u + 38 << 1) | 0
                }
                B = (Z(b[k >> 1] | 0, h) | 0) + g | 0;
                B = (Z((B << 1) + 32768 >> 16, (Z(b[j >> 1] << 1, b[f >> 1] | 0) | 0) >> 16) | 0) >>> 15 & 65535;
                b[a >> 1] = B;
                b[e >> 1] = B;
                e = (v << 16) + 131072 | 0;
                if ((e | 0) < 2621440) v = e >> 16; else break
            }
            i = z;
            return
        }

        function gc(a, d, e, f, g, h, j) {
            a = a | 0;
            d = d | 0;
            e = e | 0;
            f = f | 0;
            g = g | 0;
            h = h | 0;
            j = j | 0;
            var k = 0, l = 0, m = 0, n = 0, o = 0, p = 0, q = 0, r = 0;
            r = i;
            i = i + 160 | 0;
            q = r;
            if (g << 16 >> 16 > 0) {
                o = h & 65535;
                p = 0;
                k = 5;
                do {
                    if ((p | 0) < 40) {
                        n = p;
                        m = p & 65535;
                        h = 0;
                        while (1) {
                            if (m << 16 >> 16 < 40) {
                                m = m << 16 >> 16;
                                l = 0;
                                do {
                                    l = (Z(b[a + (m - n << 1) >> 1] | 0, b[d + (m << 1) >> 1] | 0) | 0) + l | 0;
                                    m = m + 1 | 0
                                } while ((m & 65535) << 16 >> 16 != 40)
                            } else l = 0;
                            l = l << 1;
                            c[q + (n << 2) >> 2] = l;
                            l = Gc(l) | 0;
                            h = (l | 0) > (h | 0) ? l : h;
                            l = n + o | 0;
                            m = l & 65535;
                            if (m << 16 >> 16 >= 40) break; else n = l << 16 >> 16
                        }
                    } else h = 0;
                    k = (h >> 1) + k | 0;
                    p = p + 1 | 0
                } while ((p & 65535) << 16 >> 16 != g << 16 >> 16)
            } else k = 5;
            f = ((pe(k) | 0) & 65535) - (f & 65535) | 0;
            h = f << 16 >> 16;
            l = 0 - h << 16;
            k = (l | 0) < 2031616;
            l = l >> 16;
            if ((f & 65535) << 16 >> 16 > 0) if (k) {
                k = 0;
                do {
                    f = c[q + (k << 2) >> 2] | 0;
                    d = f << h;
                    b[e + (k << 1) >> 1] = Ce((d >> h | 0) == (f | 0) ? d : f >> 31 ^ 2147483647, j) | 0;
                    k = k + 1 | 0
                } while ((k | 0) != 40);
                i = r;
                return
            } else {
                _abort();//fix cc 精简
            } else if (k) {
                k = 0;
                do {
                    b[e + (k << 1) >> 1] = Ce(c[q + (k << 2) >> 2] >> l, j) | 0;
                    k = k + 1 | 0
                } while ((k | 0) != 40);
                i = r;
                return
            } else {
                _abort();//fix cc 精简
            }
        }

        function hc(a, d, e, f, g) {
            a = a | 0;
            d = d | 0;
            e = e | 0;
            f = f | 0;
            g = g | 0;
            var h = 0, j = 0, k = 0, l = 0, m = 0, n = 0, o = 0, p = 0, q = 0, r = 0, s = 0, t = 0, u = 0, v = 0, w = 0,
                x = 0, y = 0, z = 0;
            z = i;
            i = i + 160 | 0;
            y = z;
            v = a + 2 | 0;
            w = b[a >> 1] | 0;
            x = 0;
            g = 5;
            do {
                u = x;
                k = 0;
                while (1) {
                    n = d + (u << 1) | 0;
                    t = 40 - u | 0;
                    h = (t + 131071 | 0) >>> 1 & 65535;
                    l = d + (u + 1 << 1) | 0;
                    j = Z(b[n >> 1] << 1, w) | 0;
                    if (!(h << 16 >> 16)) h = v; else {
                        s = 131111 - u + 131070 & 131070;
                        r = u + s | 0;
                        q = v;
                        p = a;
                        o = n;
                        while (1) {
                            m = o + 4 | 0;
                            n = p + 4 | 0;
                            j = (Z(b[l >> 1] << 1, b[q >> 1] | 0) | 0) + j | 0;
                            h = h + -1 << 16 >> 16;
                            j = (Z(b[m >> 1] << 1, b[n >> 1] | 0) | 0) + j | 0;
                            if (!(h << 16 >> 16)) break; else {
                                l = o + 6 | 0;
                                q = p + 6 | 0;
                                p = n;
                                o = m
                            }
                        }
                        l = d + (r + 3 << 1) | 0;
                        h = a + (s + 3 << 1) | 0
                    }
                    if (!(t & 1)) j = (Z(b[l >> 1] << 1, b[h >> 1] | 0) | 0) + j | 0;
                    c[y + (u << 2) >> 2] = j;
                    j = (j | 0) < 0 ? 0 - j | 0 : j;
                    k = (j | 0) > (k | 0) ? j : k;
                    j = u + 5 | 0;
                    if ((j & 65535) << 16 >> 16 < 40) u = j << 16 >> 16; else break
                }
                g = (k >> 1) + g | 0;
                x = x + 1 | 0
            } while ((x | 0) != 5);
            f = ((pe(g) | 0) & 65535) - (f & 65535) | 0;
            j = f << 16 >> 16;
            g = 0 - j << 16;
            k = g >> 16;
            if ((f & 65535) << 16 >> 16 > 0) {
                h = 20;
                g = y;
                while (1) {
                    y = c[g >> 2] | 0;
                    f = y << j;
                    b[e >> 1] = (((f >> j | 0) == (y | 0) ? f : y >> 31 ^ 2147483647) + 32768 | 0) >>> 16;
                    y = c[g + 4 >> 2] | 0;
                    f = y << j;
                    b[e + 2 >> 1] = (((f >> j | 0) == (y | 0) ? f : y >> 31 ^ 2147483647) + 32768 | 0) >>> 16;
                    h = h + -1 << 16 >> 16;
                    if (!(h << 16 >> 16)) break; else {
                        e = e + 4 | 0;
                        g = g + 8 | 0
                    }
                }
                i = z;
                return
            }
            if ((g | 0) < 2031616) {
                h = 20;
                g = y;
                while (1) {
                    b[e >> 1] = ((c[g >> 2] >> k) + 32768 | 0) >>> 16;
                    b[e + 2 >> 1] = ((c[g + 4 >> 2] >> k) + 32768 | 0) >>> 16;
                    h = h + -1 << 16 >> 16;
                    if (!(h << 16 >> 16)) break; else {
                        e = e + 4 | 0;
                        g = g + 8 | 0
                    }
                }
                i = z;
                return
            } else {
                _abort();//fix cc 精简
            }
        }

        function ic(a, b, d, e) {
            a = a | 0;
            b = b | 0;
            d = d | 0;
            e = e | 0;
            var f = 0, g = 0, h = 0;
            h = (Td(16383, b) | 0) << 16 >> 16;
            b = Z(h, b << 16 >> 16) | 0;
            if ((b | 0) == 1073741824) {
                c[e >> 2] = 1;
                f = 2147483647
            } else f = b << 1;
            g = (Z(h, d << 16 >> 16) | 0) >> 15;
            b = f + (g << 1) | 0;
            if ((f ^ g | 0) > 0 & (b ^ f | 0) < 0) {
                c[e >> 2] = 1;
                b = (f >>> 31) + 2147483647 | 0
            }
            f = 2147483647 - b | 0;
            d = f >> 16;
            b = Z(d, h) | 0;
            if ((b | 0) == 1073741824) {
                c[e >> 2] = 1;
                g = 2147483647
            } else g = b << 1;
            h = (Z((f >>> 1) - (d << 15) << 16 >> 16, h) | 0) >> 15;
            b = g + (h << 1) | 0;
            if ((g ^ h | 0) > 0 & (b ^ g | 0) < 0) {
                c[e >> 2] = 1;
                b = (g >>> 31) + 2147483647 | 0
            }
            g = b >> 16;
            h = a >> 16;
            d = Z(g, h) | 0;
            d = (d | 0) == 1073741824 ? 2147483647 : d << 1;
            f = (Z((b >>> 1) - (g << 15) << 16 >> 16, h) | 0) >> 15;
            e = (f << 1) + d | 0;
            e = (f ^ d | 0) > 0 & (e ^ d | 0) < 0 ? (d >>> 31) + 2147483647 | 0 : e;
            h = (Z(g, (a >>> 1) - (h << 15) << 16 >> 16) | 0) >> 15;
            a = e + (h << 1) | 0;
            a = (e ^ h | 0) > 0 & (a ^ e | 0) < 0 ? (e >>> 31) + 2147483647 | 0 : a;
            e = a << 2;
            return ((e >> 2 | 0) == (a | 0) ? e : a >> 31 ^ 2147483647) | 0
        }

        function jc(a, d) {
            a = a | 0;
            d = d | 0;
            var e = 0, f = 0, g = 0, h = 0;
            if (!a) {
                h = -1;
                return h | 0
            }
            c[a >> 2] = 0;
            e = Je(192) | 0;
            if (!e) {
                h = -1;
                return h | 0
            }
            f = e + 176 | 0;
            b[f >> 1] = 0;
            b[f + 2 >> 1] = 0;
            b[f + 4 >> 1] = 0;
            b[f + 6 >> 1] = 0;
            b[f + 8 >> 1] = 0;
            b[f + 10 >> 1] = 0;
            f = e;
            g = d;
            h = f + 20 | 0;
            do {
                b[f >> 1] = b[g >> 1] | 0;
                f = f + 2 | 0;
                g = g + 2 | 0
            } while ((f | 0) < (h | 0));
            f = e + 20 | 0;
            g = d;
            h = f + 20 | 0;
            do {
                b[f >> 1] = b[g >> 1] | 0;
                f = f + 2 | 0;
                g = g + 2 | 0
            } while ((f | 0) < (h | 0));
            f = e + 40 | 0;
            g = d;
            h = f + 20 | 0;
            do {
                b[f >> 1] = b[g >> 1] | 0;
                f = f + 2 | 0;
                g = g + 2 | 0
            } while ((f | 0) < (h | 0));
            f = e + 60 | 0;
            g = d;
            h = f + 20 | 0;
            do {
                b[f >> 1] = b[g >> 1] | 0;
                f = f + 2 | 0;
                g = g + 2 | 0
            } while ((f | 0) < (h | 0));
            f = e + 80 | 0;
            g = d;
            h = f + 20 | 0;
            do {
                b[f >> 1] = b[g >> 1] | 0;
                f = f + 2 | 0;
                g = g + 2 | 0
            } while ((f | 0) < (h | 0));
            f = e + 100 | 0;
            g = d;
            h = f + 20 | 0;
            do {
                b[f >> 1] = b[g >> 1] | 0;
                f = f + 2 | 0;
                g = g + 2 | 0
            } while ((f | 0) < (h | 0));
            f = e + 120 | 0;
            g = d;
            h = f + 20 | 0;
            do {
                b[f >> 1] = b[g >> 1] | 0;
                f = f + 2 | 0;
                g = g + 2 | 0
            } while ((f | 0) < (h | 0));
            f = e + 140 | 0;
            g = d;
            h = f + 20 | 0;
            do {
                b[f >> 1] = b[g >> 1] | 0;
                f = f + 2 | 0;
                g = g + 2 | 0
            } while ((f | 0) < (h | 0));
            f = e + 160 | 0;
            h = f + 20 | 0;
            do {
                b[f >> 1] = 0;
                f = f + 2 | 0
            } while ((f | 0) < (h | 0));
            b[e + 188 >> 1] = 7;
            b[e + 190 >> 1] = 32767;
            c[a >> 2] = e;
            h = 0;
            return h | 0
        }

        function kc(a, c) {
            a = a | 0;
            c = c | 0;
            var d = 0, e = 0, f = 0;
            if (!a) {
                f = -1;
                return f | 0
            }
            d = a + 176 | 0;
            b[d >> 1] = 0;
            b[d + 2 >> 1] = 0;
            b[d + 4 >> 1] = 0;
            b[d + 6 >> 1] = 0;
            b[d + 8 >> 1] = 0;
            b[d + 10 >> 1] = 0;
            d = a;
            e = c;
            f = d + 20 | 0;
            do {
                b[d >> 1] = b[e >> 1] | 0;
                d = d + 2 | 0;
                e = e + 2 | 0
            } while ((d | 0) < (f | 0));
            d = a + 20 | 0;
            e = c;
            f = d + 20 | 0;
            do {
                b[d >> 1] = b[e >> 1] | 0;
                d = d + 2 | 0;
                e = e + 2 | 0
            } while ((d | 0) < (f | 0));
            d = a + 40 | 0;
            e = c;
            f = d + 20 | 0;
            do {
                b[d >> 1] = b[e >> 1] | 0;
                d = d + 2 | 0;
                e = e + 2 | 0
            } while ((d | 0) < (f | 0));
            d = a + 60 | 0;
            e = c;
            f = d + 20 | 0;
            do {
                b[d >> 1] = b[e >> 1] | 0;
                d = d + 2 | 0;
                e = e + 2 | 0
            } while ((d | 0) < (f | 0));
            d = a + 80 | 0;
            e = c;
            f = d + 20 | 0;
            do {
                b[d >> 1] = b[e >> 1] | 0;
                d = d + 2 | 0;
                e = e + 2 | 0
            } while ((d | 0) < (f | 0));
            d = a + 100 | 0;
            e = c;
            f = d + 20 | 0;
            do {
                b[d >> 1] = b[e >> 1] | 0;
                d = d + 2 | 0;
                e = e + 2 | 0
            } while ((d | 0) < (f | 0));
            d = a + 120 | 0;
            e = c;
            f = d + 20 | 0;
            do {
                b[d >> 1] = b[e >> 1] | 0;
                d = d + 2 | 0;
                e = e + 2 | 0
            } while ((d | 0) < (f | 0));
            d = a + 140 | 0;
            e = c;
            f = d + 20 | 0;
            do {
                b[d >> 1] = b[e >> 1] | 0;
                d = d + 2 | 0;
                e = e + 2 | 0
            } while ((d | 0) < (f | 0));
            d = a + 160 | 0;
            f = d + 20 | 0;
            do {
                b[d >> 1] = 0;
                d = d + 2 | 0
            } while ((d | 0) < (f | 0));
            b[a + 188 >> 1] = 7;
            b[a + 190 >> 1] = 32767;
            f = 1;
            return f | 0
        }

        function lc(a) {
            a = a | 0;
            var b = 0;
            if (!a) return;
            b = c[a >> 2] | 0;
            if (!b) return;
            Ke(b);
            c[a >> 2] = 0;
            return
        }

        //fix cc 精简

        function nc(a, d, f, g) {
            a = a | 0;
            d = d | 0;
            f = f | 0;
            g = g | 0;
            var h = 0, j = 0, k = 0, l = 0, m = 0, n = 0;
            n = i;
            i = i + 16 | 0;
            k = n + 2 | 0;
            m = n;
            l = a + 176 | 0;
            j = (e[l >> 1] | 0) + 1 | 0;
            j = (j & 65535 | 0) == 8 ? 0 : j & 65535;
            b[l >> 1] = j;
            j = a + ((j << 16 >> 16) * 10 << 1) | 0;
            h = j + 20 | 0;
            do {
                b[j >> 1] = b[d >> 1] | 0;
                j = j + 2 | 0;
                d = d + 2 | 0
            } while ((j | 0) < (h | 0));
            d = 0;
            h = 160;
            while (1) {
                j = b[f >> 1] | 0;
                d = (Z(j << 1, j) | 0) + d | 0;
                if ((d | 0) < 0) {
                    d = 2147483647;
                    break
                }
                h = h + -1 << 16 >> 16;
                if (!(h << 16 >> 16)) break; else f = f + 2 | 0
            }
            de(d, k, m, g);
            d = b[k >> 1] | 0;
            k = d << 16 >> 16;
            f = k << 10;
            if ((f | 0) != (k << 26 >> 16 | 0)) {
                c[g >> 2] = 1;
                f = d << 16 >> 16 > 0 ? 32767 : -32768
            }
            b[a + 160 + (b[l >> 1] << 1) >> 1] = (((b[m >> 1] | 0) >>> 5) + f << 16) + -558432256 >> 17;
            i = n;
            return
        }

        //fix cc 精简

        function pc(a, b, c, d, e, f, g, h) {
            a = a | 0;
            b = b | 0;
            c = c | 0;
            d = d | 0;
            e = e | 0;
            f = f | 0;
            g = g | 0;
            h = h | 0;
            if (!(f << 16 >> 16)) {
                f = a << 16 >> 16;
                if (((f << 16) + -5570560 | 0) < 65536) {
                    b = (f * 3 | 0) + -58 + (b << 16 >> 16) | 0;
                    b = b & 65535;
                    return b | 0
                } else {
                    b = f + 112 | 0;
                    b = b & 65535;
                    return b | 0
                }
            }
            if (!(g << 16 >> 16)) {
                h = (a & 65535) - (d & 65535) << 16;
                b = (b << 16 >> 16) + 2 + (h >> 15) + (h >> 16) | 0;
                b = b & 65535;
                return b | 0
            }
            d = d << 16 >> 16;
            d = (((c & 65535) - d << 16) + -327680 | 0) > 0 ? d + 5 & 65535 : c;
            e = e << 16 >> 16;
            c = a << 16 >> 16;
            d = (((e - (d & 65535) << 16) + -262144 | 0) > 0 ? e + 65532 & 65535 : d) << 16 >> 16;
            e = d * 196608 | 0;
            a = e + -393216 >> 16;
            f = ((b & 65535) << 16) + (c * 196608 | 0) >> 16;
            if (!(a - f & 32768)) {
                b = c + 5 - d | 0;
                b = b & 65535;
                return b | 0
            }
            if ((e + 196608 >> 16 | 0) > (f | 0)) {
                b = f + 3 - a | 0;
                b = b & 65535;
                return b | 0
            } else {
                b = c + 11 - d | 0;
                b = b & 65535;
                return b | 0
            }
            return 0
        }

        function qc(a, b, c, d, e) {
            a = a | 0;
            b = b | 0;
            c = c | 0;
            d = d | 0;
            e = e | 0;
            e = a << 16 >> 16;
            do if (!(d << 16 >> 16)) if (a << 16 >> 16 < 95) {
                e = ((e * 393216 | 0) + -6881280 >> 16) + (b << 16 >> 16) | 0;
                break
            } else {
                e = e + 368 | 0;
                break
            } else e = ((((e - (c & 65535) | 0) * 393216 | 0) + 196608 | 0) >>> 16) + (b & 65535) | 0; while (0);
            return e & 65535 | 0
        }

        //fix cc 精简

        function tc(d, f, g, h) {
            d = d | 0;
            f = f | 0;
            g = g | 0;
            h = h | 0;
            var i = 0, j = 0, k = 0, l = 0, m = 0, n = 0, o = 0, p = 0;
            o = c[h + 100 >> 2] | 0;
            n = c[h + 96 >> 2] | 0;
            a[g >> 0] = d << 3;
            n = n + (d << 1) | 0;
            i = b[n >> 1] | 0;
            if (d >>> 0 >= 8) {
                _abort();//fix cc 精简
            }
            k = i << 16 >> 16;
            if (i << 16 >> 16 > 7) {
                i = o + (d << 2) | 0;
                h = 0;
                m = 0;
                j = 1;
                while (1) {
                    p = e[f + (b[(c[i >> 2] | 0) + (h << 1) >> 1] << 1) >> 1] << 7;
                    k = g + (j << 16 >> 16) | 0;
                    a[k >> 0] = p;
                    p = e[f + (b[(c[i >> 2] | 0) + ((m | 1) << 16 >> 16 << 1) >> 1] << 1) >> 1] << 6 | p;
                    a[k >> 0] = p;
                    p = e[f + (b[(c[i >> 2] | 0) + ((m | 2) << 16 >> 16 << 1) >> 1] << 1) >> 1] << 5 | p;
                    a[k >> 0] = p;
                    p = e[f + (b[(c[i >> 2] | 0) + ((m | 3) << 16 >> 16 << 1) >> 1] << 1) >> 1] << 4 | p;
                    a[k >> 0] = p;
                    p = e[f + (b[(c[i >> 2] | 0) + ((m | 4) << 16 >> 16 << 1) >> 1] << 1) >> 1] << 3 | p & 240;
                    a[k >> 0] = p;
                    p = e[f + (b[(c[i >> 2] | 0) + ((m | 5) << 16 >> 16 << 1) >> 1] << 1) >> 1] << 2 | p;
                    a[k >> 0] = p;
                    p = e[f + (b[(c[i >> 2] | 0) + ((m | 6) << 16 >> 16 << 1) >> 1] << 1) >> 1] << 1 | p;
                    a[k >> 0] = p;
                    l = m + 8 << 16 >> 16;
                    j = j + 1 << 16 >> 16;
                    a[k >> 0] = p & 254 | e[f + (b[(c[i >> 2] | 0) + ((m | 7) << 16 >> 16 << 1) >> 1] << 1) >> 1];
                    h = l << 16 >> 16;
                    k = b[n >> 1] | 0;
                    if ((h | 0) >= (k + -7 | 0)) break; else m = l
                }
            } else {
                l = 0;
                j = 1
            }
            n = k & 7;
            m = g + (j << 16 >> 16) | 0;
            a[m >> 0] = 0;
            if (!n) return;
            j = o + (d << 2) | 0;
            i = 0;
            h = 0;
            k = 0;
            while (1) {
                h = (e[f + (b[(c[j >> 2] | 0) + (l << 16 >> 16 << 1) >> 1] << 1) >> 1] & 255) << 7 - i | h & 255;
                a[m >> 0] = h;
                k = k + 1 << 16 >> 16;
                i = k << 16 >> 16;
                if ((i | 0) >= (n | 0)) break; else l = l + 1 << 16 >> 16
            }
            return
        }

        function uc(a) {
            a = a | 0;
            var d = 0;
            if (!a) {
                a = -1;
                return a | 0
            }
            c[a >> 2] = 0;
            d = Je(16) | 0;
            if (!d) {
                a = -1;
                return a | 0
            }
            ;b[d >> 1] = 0;
            b[d + 2 >> 1] = 0;
            b[d + 4 >> 1] = 0;
            b[d + 6 >> 1] = 0;
            b[d + 8 >> 1] = 0;
            b[d + 10 >> 1] = 0;
            b[d + 12 >> 1] = 0;
            b[d + 14 >> 1] = 0;
            c[a >> 2] = d;
            a = 0;
            return a | 0
        }

        function vc(a) {
            a = a | 0;
            if (!a) {
                a = -1;
                return a | 0
            }
            ;b[a >> 1] = 0;
            b[a + 2 >> 1] = 0;
            b[a + 4 >> 1] = 0;
            b[a + 6 >> 1] = 0;
            b[a + 8 >> 1] = 0;
            b[a + 10 >> 1] = 0;
            b[a + 12 >> 1] = 0;
            b[a + 14 >> 1] = 0;
            a = 0;
            return a | 0
        }

        function wc(a) {
            a = a | 0;
            var b = 0;
            if (!a) return;
            b = c[a >> 2] | 0;
            if (!b) return;
            Ke(b);
            c[a >> 2] = 0;
            return
        }

        function xc(a, d, e, f, g) {
            a = a | 0;
            d = d | 0;
            e = e | 0;
            f = f | 0;
            g = g | 0;
            var h = 0, i = 0, j = 0, k = 0, l = 0;
            j = d << 16 >> 16 < 2722 ? 0 : d << 16 >> 16 < 5444 ? 1 : 2;
            i = Ee(e, 1, g) | 0;
            l = a + 4 | 0;
            if (!(e << 16 >> 16 > 200 ? i << 16 >> 16 > (b[l >> 1] | 0) : 0)) {
                i = b[a >> 1] | 0;
                if (i << 16 >> 16) {
                    h = i + -1 << 16 >> 16;
                    b[a >> 1] = h;
                    h = h << 16 >> 16 != 0;
                    k = 5
                }
            } else {
                b[a >> 1] = 8;
                h = 1;
                k = 5
            }
            if ((k | 0) == 5) if ((j & 65535) < 2 & h) j = (j & 65535) + 1 & 65535;
            k = a + 6 | 0;
            b[k >> 1] = d;
            h = Zd(k, 5) | 0;
            if (!(j << 16 >> 16 != 0 | h << 16 >> 16 > 5443)) if (h << 16 >> 16 < 0) h = 16384; else {
                h = h << 16 >> 16;
                h = (((h << 18 >> 18 | 0) == (h | 0) ? h << 2 : h >>> 15 ^ 32767) << 16 >> 16) * 24660 >> 15;
                if ((h | 0) > 32767) {
                    c[g >> 2] = 1;
                    h = 32767
                }
                h = 16384 - h & 65535
            } else h = 0;
            i = a + 2 | 0;
            if (!(b[i >> 1] | 0)) h = De(h, 1, g) | 0;
            b[f >> 1] = h;
            b[i >> 1] = h;
            b[l >> 1] = e;
            f = a + 12 | 0;
            b[a + 14 >> 1] = b[f >> 1] | 0;
            e = a + 10 | 0;
            b[f >> 1] = b[e >> 1] | 0;
            a = a + 8 | 0;
            b[e >> 1] = b[a >> 1] | 0;
            b[a >> 1] = b[k >> 1] | 0;
            return
        }

        function yc(a) {
            a = a | 0;
            var d = 0, e = 0, f = 0, g = 0, h = 0, i = 0;
            if (!a) {
                a = -1;
                return a | 0
            }
            c[a >> 2] = 0;
            d = Je(68) | 0;
            f = d;
            if (!d) {
                a = -1;
                return a | 0
            }
            c[d + 28 >> 2] = 0;
            g = d + 64 | 0;
            c[g >> 2] = 0;
            h = d + 32 | 0;
            if (((Ud(h) | 0) << 16 >> 16 == 0 ? (i = d + 48 | 0, (Ud(i) | 0) << 16 >> 16 == 0) : 0) ? (uc(g) | 0) << 16 >> 16 == 0 : 0) {
                e = d + 32 | 0;
                do {
                    b[d >> 1] = 0;
                    d = d + 2 | 0
                } while ((d | 0) < (e | 0));
                Ud(h) | 0;
                Ud(i) | 0;
                vc(c[g >> 2] | 0) | 0;
                c[a >> 2] = f;
                a = 0;
                return a | 0
            }
            wc(g);
            Ke(d);
            a = -1;
            return a | 0
        }

        function zc(a) {
            a = a | 0;
            var b = 0;
            if (!a) return;
            b = c[a >> 2] | 0;
            if (!b) return;
            wc(b + 64 | 0);
            Ke(c[a >> 2] | 0);
            c[a >> 2] = 0;
            return
        }

        function Ac(a) {
            a = a | 0;
            var d = 0, e = 0, f = 0;
            if (!a) {
                f = -1;
                return f | 0
            }
            d = a + 32 | 0;
            e = a;
            f = e + 32 | 0;
            do {
                b[e >> 1] = 0;
                e = e + 2 | 0
            } while ((e | 0) < (f | 0));
            Ud(d) | 0;
            Ud(a + 48 | 0) | 0;
            vc(c[a + 64 >> 2] | 0) | 0;
            f = 0;
            return f | 0
        }

        function Bc(a, d, f, g, h, j, k, l, m, n, o, p, q, r, s, t, u, v, w) {
            a = a | 0;
            d = d | 0;
            f = f | 0;
            g = g | 0;
            h = h | 0;
            j = j | 0;
            k = k | 0;
            l = l | 0;
            m = m | 0;
            n = n | 0;
            o = o | 0;
            p = p | 0;
            q = q | 0;
            r = r | 0;
            s = s | 0;
            t = t | 0;
            u = u | 0;
            v = v | 0;
            w = w | 0;
            var x = 0, y = 0, z = 0, A = 0, B = 0, C = 0, D = 0, E = 0, F = 0, G = 0, H = 0;
            H = i;
            i = i + 48 | 0;
            y = H + 34 | 0;
            A = H + 32 | 0;
            C = H + 30 | 0;
            B = H + 28 | 0;
            z = H + 18 | 0;
            x = H + 8 | 0;
            D = H + 6 | 0;
            E = H + 4 | 0;
            F = H + 2 | 0;
            G = H;
            if (d) {
                o = a + 32 | 0;
                Vd(o, d, h, y, A, D, E, w);
                do if ((d | 0) != 7) {
                    Vb(d, j, k, l, m, n, z, x, G, F, w);
                    if ((d | 0) == 5) {
                        ld(c[a + 64 >> 2] | 0, f, g, h, z, x, b[D >> 1] | 0, b[E >> 1] | 0, b[y >> 1] | 0, b[A >> 1] | 0, 40, b[G >> 1] | 0, b[F >> 1] | 0, p, s, t, C, B, u, v, w);
                        break
                    } else {
                        a = od(d, b[y >> 1] | 0, b[A >> 1] | 0, z, x, p, s, t, C, B, v, w) | 0;
                        j = c[u >> 2] | 0;
                        c[u >> 2] = j + 2;
                        b[j >> 1] = a;
                        break
                    }
                } else {
                    b[t >> 1] = Cc(k, m, w) | 0;
                    a = md(7, b[y >> 1] | 0, b[A >> 1] | 0, t, C, B, c[v + 68 >> 2] | 0, w) | 0;
                    j = c[u >> 2] | 0;
                    c[u >> 2] = j + 2;
                    b[j >> 1] = a
                } while (0);
                Wd(o, b[C >> 1] | 0, b[B >> 1] | 0);
                i = H;
                return
            }
            if (!(o << 16 >> 16)) {
                Vd(a + 48 | 0, 0, h, y, A, D, E, w);
                Vb(0, j, k, l, m, n, z, x, G, F, w);
                Wb(j, D, E, w);
                j = jd(a + 32 | 0, b[a >> 1] | 0, b[a + 2 >> 1] | 0, a + 8 | 0, a + 18 | 0, b[a + 4 >> 1] | 0, b[a + 6 >> 1] | 0, h, b[y >> 1] | 0, b[A >> 1] | 0, x, z, b[D >> 1] | 0, b[E >> 1] | 0, p, q, r, s, t, w) | 0;
                b[c[a + 28 >> 2] >> 1] = j;
                i = H;
                return
            }
            o = c[u >> 2] | 0;
            c[u >> 2] = o + 2;
            c[a + 28 >> 2] = o;
            o = a + 48 | 0;
            f = a + 32 | 0;
            q = f;
            q = e[q >> 1] | e[q + 2 >> 1] << 16;
            f = f + 4 | 0;
            f = e[f >> 1] | e[f + 2 >> 1] << 16;
            u = o;
            r = u;
            b[r >> 1] = q;
            b[r + 2 >> 1] = q >>> 16;
            u = u + 4 | 0;
            b[u >> 1] = f;
            b[u + 2 >> 1] = f >>> 16;
            u = a + 40 | 0;
            f = u;
            f = e[f >> 1] | e[f + 2 >> 1] << 16;
            u = u + 4 | 0;
            u = e[u >> 1] | e[u + 2 >> 1] << 16;
            r = a + 56 | 0;
            q = r;
            b[q >> 1] = f;
            b[q + 2 >> 1] = f >>> 16;
            r = r + 4 | 0;
            b[r >> 1] = u;
            b[r + 2 >> 1] = u >>> 16;
            r = a + 2 | 0;
            Vd(o, 0, h, a, r, D, E, w);
            Vb(0, j, k, l, m, n, a + 18 | 0, a + 8 | 0, G, F, w);
            l = (e[F >> 1] | 0) + 1 | 0;
            u = b[G >> 1] | 0;
            q = l << 16 >> 16;
            if ((l & 65535) << 16 >> 16 < 0) {
                v = 0 - q << 16;
                if ((v | 0) < 983040) v = u << 16 >> 16 >> (v >> 16) & 65535; else v = 0
            } else {
                u = u << 16 >> 16;
                v = u << q;
                if ((v << 16 >> 16 >> q | 0) == (u | 0)) v = v & 65535; else v = (u >>> 15 ^ 32767) & 65535
            }
            b[t >> 1] = v;
            Wb(j, a + 4 | 0, a + 6 | 0, w);
            id(o, b[a >> 1] | 0, b[r >> 1] | 0, b[F >> 1] | 0, b[G >> 1] | 0, w);
            i = H;
            return
        }

        function Cc(a, c, d) {
            a = a | 0;
            c = c | 0;
            d = d | 0;
            var e = 0, f = 0, g = 0;
            f = 10;
            d = a;
            e = c;
            a = 0;
            while (1) {
                a = (Z(b[e >> 1] >> 1, b[d >> 1] | 0) | 0) + a | 0;
                a = a + (Z(b[e + 2 >> 1] >> 1, b[d + 2 >> 1] | 0) | 0) | 0;
                a = a + (Z(b[e + 4 >> 1] >> 1, b[d + 4 >> 1] | 0) | 0) | 0;
                a = a + (Z(b[e + 6 >> 1] >> 1, b[d + 6 >> 1] | 0) | 0) | 0;
                f = f + -1 << 16 >> 16;
                if (!(f << 16 >> 16)) break; else {
                    d = d + 8 | 0;
                    e = e + 8 | 0
                }
            }
            d = a << 1;
            f = pe(d | 1) | 0;
            g = f << 16 >> 16;
            d = (f << 16 >> 16 < 17 ? d >> 17 - g : d << g + -17) & 65535;
            if (d << 16 >> 16 < 1) {
                c = 0;
                return c | 0
            } else {
                f = 20;
                e = c;
                a = 0
            }
            while (1) {
                c = b[e >> 1] >> 1;
                c = ((Z(c, c) | 0) >>> 2) + a | 0;
                a = b[e + 2 >> 1] >> 1;
                a = c + ((Z(a, a) | 0) >>> 2) | 0;
                f = f + -1 << 16 >> 16;
                if (!(f << 16 >> 16)) break; else e = e + 4 | 0
            }
            a = a << 3;
            f = pe(a) | 0;
            c = f << 16 >> 16;
            d = Td(d, (f << 16 >> 16 < 16 ? a >> 16 - c : a << c + -16) & 65535) | 0;
            c = (g << 16) + 327680 - (c << 16) | 0;
            a = c >> 16;
            if ((c | 0) > 65536) a = d << 16 >> 16 >> a + -1; else a = d << 16 >> 16 << 1 - a;
            c = a & 65535;
            return c | 0
        }

        function Dc(a, d, e, f, g, h) {
            a = a | 0;
            d = d | 0;
            e = e | 0;
            f = f | 0;
            g = g | 0;
            h = h | 0;
            var i = 0, j = 0, k = 0, l = 0, m = 0, n = 0, o = 0, p = 0, q = 0, r = 0;
            c[h >> 2] = 0;
            m = g << 16 >> 16;
            k = m >>> 2 & 65535;
            o = k << 16 >> 16 == 0;
            if (o) j = 0; else {
                l = k;
                i = e;
                j = 0;
                while (1) {
                    p = b[i >> 1] | 0;
                    p = (Z(p, p) | 0) + j | 0;
                    j = b[i + 2 >> 1] | 0;
                    j = p + (Z(j, j) | 0) | 0;
                    p = b[i + 4 >> 1] | 0;
                    p = j + (Z(p, p) | 0) | 0;
                    j = b[i + 6 >> 1] | 0;
                    j = p + (Z(j, j) | 0) | 0;
                    l = l + -1 << 16 >> 16;
                    if (!(l << 16 >> 16)) break; else i = i + 8 | 0
                }
            }
            if (!((j >>> 31 ^ 1) & (j | 0) < 1073741824)) {//不可精简
                j = m >>> 1 & 65535;
                if (!(j << 16 >> 16)) j = 1; else {
                    i = j;
                    l = e;
                    j = 0;
                    while (1) {
                        p = b[l >> 1] >> 2;
                        p = (Z(p, p) | 0) + j | 0;
                        j = b[l + 2 >> 1] >> 2;
                        j = p + (Z(j, j) | 0) | 0;
                        i = i + -1 << 16 >> 16;
                        if (!(i << 16 >> 16)) break; else l = l + 4 | 0
                    }
                    j = j << 1 | 1
                }
                p = (pe(j) | 0) << 16 >> 16;
                n = p + 65532 & 65535;
                p = Ce(j << p, h) | 0
            } else {
                m = j << 1 | 1;
                p = pe(m) | 0;
                n = p;
                p = Ce(m << (p << 16 >> 16), h) | 0
            }
            c[h >> 2] = 0;
            do if (!(g << 16 >> 16)) {
                j = 1;
                q = 14
            } else {
                m = g;
                l = d;
                j = e;
                g = 0;
                while (1) {
                    r = Z(b[j >> 1] | 0, b[l >> 1] | 0) | 0;
                    i = r + g | 0;
                    if ((r ^ g | 0) > 0 & (i ^ g | 0) < 0) break;
                    m = m + -1 << 16 >> 16;
                    if (!(m << 16 >> 16)) {
                        q = 13;
                        break
                    } else {
                        l = l + 2 | 0;
                        j = j + 2 | 0;
                        g = i
                    }
                }
                if ((q | 0) == 13) {
                    j = i << 1 | 1;
                    q = 14;
                    break
                }
                c[h >> 2] = 1;
                if (o) j = 1; else {//不可精简
                    j = d;
                    i = 0;
                    while (1) {
                        i = (Z(b[e >> 1] >> 2, b[j >> 1] | 0) | 0) + i | 0;
                        i = i + (Z(b[e + 2 >> 1] >> 2, b[j + 2 >> 1] | 0) | 0) | 0;
                        i = i + (Z(b[e + 4 >> 1] >> 2, b[j + 4 >> 1] | 0) | 0) | 0;
                        i = i + (Z(b[e + 6 >> 1] >> 2, b[j + 6 >> 1] | 0) | 0) | 0;
                        k = k + -1 << 16 >> 16;
                        if (!(k << 16 >> 16)) break; else {
                            j = j + 8 | 0;
                            e = e + 8 | 0
                        }
                    }
                    j = i << 1 | 1
                }
                e = (pe(j) | 0) << 16 >> 16;
                i = e + 65532 & 65535;
                e = Ce(j << e, h) | 0
            } while (0);
            if ((q | 0) == 14) {
                e = pe(j) | 0;
                i = e;
                e = Ce(j << (e << 16 >> 16), h) | 0
            }
            b[f >> 1] = p;
            j = n << 16 >> 16;
            b[f + 2 >> 1] = 15 - j;
            b[f + 4 >> 1] = e;
            i = i << 16 >> 16;
            b[f + 6 >> 1] = 15 - i;
            if (e << 16 >> 16 < 4) {
                r = 0;
                return r | 0
            }
            i = De(Td(e << 16 >> 16 >>> 1 & 65535, p) | 0, i - j & 65535, h) | 0;
            i = i << 16 >> 16 > 19661 ? 19661 : i;
            if ((a | 0) != 7) {
                r = i;
                return r | 0
            }
            r = i & 65532;
            return r | 0
        }

        //fix cc 精简

        function Fc(a, c, d, e) {
            a = a | 0;
            c = c | 0;
            d = d | 0;
            e = e | 0;
            if (d << 16 >> 16) c = c << 16 >> 16 << 1 & 65535;
            if (c << 16 >> 16 < 0) {
                a = a + -2 | 0;
                c = (c & 65535) + 6 & 65535
            }
            d = c << 16 >> 16;
            e = 6 - d << 16 >> 16;
            c = (Z(b[3468 + (d << 1) >> 1] | 0, b[a >> 1] | 0) | 0) + 16384 | 0;
            c = c + (Z(b[3468 + (e << 1) >> 1] | 0, b[a + 2 >> 1] | 0) | 0) | 0;
            c = c + (Z(b[3468 + (d + 6 << 1) >> 1] | 0, b[a + -2 >> 1] | 0) | 0) | 0;
            c = c + (Z(b[3468 + (e + 6 << 1) >> 1] | 0, b[a + 4 >> 1] | 0) | 0) | 0;
            c = (Z(b[3468 + (d + 12 << 1) >> 1] | 0, b[a + -4 >> 1] | 0) | 0) + c | 0;
            c = c + (Z(b[3468 + (e + 12 << 1) >> 1] | 0, b[a + 6 >> 1] | 0) | 0) | 0;
            d = c + (Z(b[3468 + (d + 18 << 1) >> 1] | 0, b[a + -6 >> 1] | 0) | 0) | 0;
            return (d + (Z(b[3468 + (e + 18 << 1) >> 1] | 0, b[a + 8 >> 1] | 0) | 0) | 0) >>> 15 & 65535 | 0
        }

        function Gc(a) {
            a = a | 0;
            a = a - (a >>> 31) | 0;
            return a >> 31 ^ a | 0
        }

        function Hc(a, c, d, e) {
            a = a | 0;
            c = c | 0;
            d = d | 0;
            e = e | 0;
            var f = 0, g = 0, h = 0, i = 0, j = 0;
            if (!(a << 16 >> 16)) return; else {
                f = 3518;
                g = 3538;
                e = d
            }
            while (1) {
                e = e + 2 | 0;
                c = c + 2 | 0;
                j = b[c >> 1] | 0;
                i = b[f >> 1] | 0;
                d = Z(i, j) | 0;
                d = (d | 0) == 1073741824 ? 2147483647 : d << 1;
                j = (Z(b[g >> 1] | 0, j) | 0) >> 15;
                h = (j << 1) + d | 0;
                h = (d ^ j | 0) > 0 & (h ^ d | 0) < 0 ? (d >>> 31) + 2147483647 | 0 : h;
                i = (Z(i, b[e >> 1] | 0) | 0) >> 15;
                d = h + (i << 1) | 0;
                d = (h ^ i | 0) > 0 & (d ^ h | 0) < 0 ? (h >>> 31) + 2147483647 | 0 : d;
                b[c >> 1] = d >>> 16;
                b[e >> 1] = (d >>> 1) - (d >> 16 << 15);
                a = a + -1 << 16 >> 16;
                if (!(a << 16 >> 16)) break; else {
                    f = f + 2 | 0;
                    g = g + 2 | 0
                }
            }
            return
        }

        function Ic(a, b, d) {
            a = a | 0;
            b = b | 0;
            d = d | 0;
            var e = 0, f = 0;
            e = a & 65535;
            f = e << 16;
            b = b << 16 >> 16;
            a = (b << 1) + f | 0;
            if (!((b ^ f | 0) > 0 & (a ^ f | 0) < 0)) {
                f = a;
                return f | 0
            }
            c[d >> 2] = 1;
            f = (e >>> 15) + 2147483647 | 0;
            return f | 0
        }

        function Jc(a) {
            a = a | 0;
            var d = 0, e = 0, f = 0;
            if (!a) {
                f = -1;
                return f | 0
            }
            c[a >> 2] = 0;
            d = Je(22) | 0;
            if (!d) {
                f = -1;
                return f | 0
            }
            b[d >> 1] = 4096;
            e = d + 2 | 0;
            f = e + 20 | 0;
            do {
                b[e >> 1] = 0;
                e = e + 2 | 0
            } while ((e | 0) < (f | 0));
            c[a >> 2] = d;
            f = 0;
            return f | 0
        }

        function Kc(a) {
            a = a | 0;
            var c = 0;
            if (!a) {
                c = -1;
                return c | 0
            }
            b[a >> 1] = 4096;
            a = a + 2 | 0;
            c = a + 20 | 0;
            do {
                b[a >> 1] = 0;
                a = a + 2 | 0
            } while ((a | 0) < (c | 0));
            c = 0;
            return c | 0
        }

        function Lc(a) {
            a = a | 0;
            var b = 0;
            if (!a) return;
            b = c[a >> 2] | 0;
            if (!b) return;
            Ke(b);
            c[a >> 2] = 0;
            return
        }

        function Mc(a, c, d, f, g, h) {
            a = a | 0;
            c = c | 0;
            d = d | 0;
            f = f | 0;
            g = g | 0;
            h = h | 0;
            var j = 0, k = 0, l = 0, m = 0, n = 0, o = 0, p = 0, q = 0, r = 0, s = 0, t = 0, u = 0, v = 0, w = 0, x = 0,
                y = 0, z = 0, A = 0, B = 0, C = 0, D = 0, E = 0, F = 0, G = 0, H = 0, I = 0, J = 0, K = 0, L = 0, M = 0;
            K = i;
            i = i + 96 | 0;
            I = K + 66 | 0;
            J = K + 44 | 0;
            H = K + 22 | 0;
            k = K;
            D = c + 2 | 0;
            G = d + 2 | 0;
            F = (b[G >> 1] << 1) + (e[D >> 1] << 16) | 0;
            j = Gc(F) | 0;
            j = ic(j, b[c >> 1] | 0, b[d >> 1] | 0, h) | 0;
            if ((F | 0) > 0) j = Oc(j) | 0;
            B = j >> 16;
            b[g >> 1] = Ce(j, h) | 0;
            v = j >> 20;
            E = I + 2 | 0;
            b[E >> 1] = v;
            F = J + 2 | 0;
            b[F >> 1] = (j >>> 5) - (v << 15);
            v = Z(B, B) | 0;
            v = (v | 0) == 1073741824 ? 2147483647 : v << 1;
            B = (Z((j >>> 1) - (B << 15) << 16 >> 16, B) | 0) >> 15;
            C = B << 1;
            A = C + v | 0;
            A = (B ^ v | 0) > 0 & (A ^ v | 0) < 0 ? (v >>> 31) + 2147483647 | 0 : A;
            C = A + C | 0;
            C = 2147483647 - (Gc((A ^ B | 0) > 0 & (C ^ A | 0) < 0 ? (A >>> 31) + 2147483647 | 0 : C) | 0) | 0;
            A = C >> 16;
            B = b[c >> 1] | 0;
            v = Z(A, B) | 0;
            v = (v | 0) == 1073741824 ? 2147483647 : v << 1;
            B = (Z((C >>> 1) - (A << 15) << 16 >> 16, B) | 0) >> 15;
            C = (B << 1) + v | 0;
            C = (B ^ v | 0) > 0 & (C ^ v | 0) < 0 ? (v >>> 31) + 2147483647 | 0 : C;
            A = (Z(b[d >> 1] | 0, A) | 0) >> 15;
            v = C + (A << 1) | 0;
            v = (C ^ A | 0) > 0 & (v ^ C | 0) < 0 ? (C >>> 31) + 2147483647 | 0 : v;
            C = pe(v) | 0;
            v = v << (C << 16 >> 16);
            A = H + 2 | 0;
            B = k + 2 | 0;
            l = v;
            v = (v >>> 1) - (v >> 16 << 15) | 0;
            w = k + 4 | 0;
            x = H + 4 | 0;
            y = 2;
            z = 2;
            while (1) {
                u = l >>> 16;
                j = u & 65535;
                r = v & 65535;
                s = z + -1 | 0;
                n = I + (s << 1) | 0;
                t = J + (s << 1) | 0;
                q = 1;
                p = n;
                o = t;
                m = D;
                k = G;
                l = 0;
                while (1) {
                    L = b[m >> 1] | 0;
                    M = ((Z(b[o >> 1] | 0, L) | 0) >> 15) + l | 0;
                    l = b[p >> 1] | 0;
                    l = M + (Z(l, L) | 0) + ((Z(l, b[k >> 1] | 0) | 0) >> 15) | 0;
                    q = q + 1 << 16 >> 16;
                    if ((q << 16 >> 16 | 0) >= (z | 0)) break; else {
                        p = p + -2 | 0;
                        o = o + -2 | 0;
                        m = m + 2 | 0;
                        k = k + 2 | 0
                    }
                }
                M = (e[c + (z << 1) >> 1] << 16) + (l << 5) + (b[d + (z << 1) >> 1] << 1) | 0;
                l = ic(Gc(M) | 0, j, r, h) | 0;
                if ((M | 0) > 0) l = Oc(l) | 0;
                k = C << 16 >> 16;
                if (C << 16 >> 16 > 0) {
                    j = l << k;
                    if ((j >> k | 0) != (l | 0)) j = l >> 31 ^ 2147483647
                } else {
                    k = 0 - k << 16;
                    if ((k | 0) < 2031616) j = l >> (k >> 16); else j = 0
                }
                q = j >> 16;
                if ((z | 0) < 5) b[g + (s << 1) >> 1] = (j + 32768 | 0) >>> 16;
                M = (j >>> 16) - (j >>> 31) | 0;
                if (((M << 16 >> 31 ^ M) & 65535) << 16 >> 16 > 32750) {
                    j = 16;
                    break
                }
                o = (j >>> 1) - (q << 15) << 16 >> 16;
                p = 1;
                l = t;
                k = A;
                m = B;
                while (1) {
                    L = (Z(b[l >> 1] | 0, q) | 0) >> 15;
                    t = b[n >> 1] | 0;
                    M = (Z(t, o) | 0) >> 15;
                    t = Z(t, q) | 0;
                    M = t + L + (b[J + (p << 1) >> 1] | 0) + (b[I + (p << 1) >> 1] << 15) + M | 0;
                    b[k >> 1] = M >>> 15;
                    b[m >> 1] = M & 32767;
                    p = p + 1 | 0;
                    if ((p & 65535) << 16 >> 16 == y << 16 >> 16) break; else {
                        n = n + -2 | 0;
                        l = l + -2 | 0;
                        k = k + 2 | 0;
                        m = m + 2 | 0
                    }
                }
                b[x >> 1] = j >> 20;
                b[w >> 1] = (j >>> 5) - (b[H + (z << 1) >> 1] << 15);
                L = Z(q, q) | 0;
                L = (L | 0) == 1073741824 ? 2147483647 : L << 1;
                j = (Z(o, q) | 0) >> 15;
                M = j << 1;
                k = M + L | 0;
                k = (j ^ L | 0) > 0 & (k ^ L | 0) < 0 ? (L >>> 31) + 2147483647 | 0 : k;
                M = k + M | 0;
                M = 2147483647 - (Gc((k ^ j | 0) > 0 & (M ^ k | 0) < 0 ? (k >>> 31) + 2147483647 | 0 : M) | 0) | 0;
                k = M >> 16;
                j = u << 16 >> 16;
                j = ((Z(k, v << 16 >> 16) | 0) >> 15) + (Z(k, j) | 0) + ((Z((M >>> 1) - (k << 15) << 16 >> 16, j) | 0) >> 15) << 1;
                k = (pe(j) | 0) << 16 >> 16;
                j = j << k;
                M = z << 1;
                Oe(E | 0, A | 0, M | 0) | 0;
                Oe(F | 0, B | 0, M | 0) | 0;
                z = z + 1 | 0;
                if ((z | 0) >= 11) {
                    j = 20;
                    break
                } else {
                    C = k + (C & 65535) & 65535;
                    l = j;
                    v = (j >> 1) - (j >> 16 << 15) | 0;
                    w = w + 2 | 0;
                    x = x + 2 | 0;
                    y = y + 1 << 16 >> 16
                }
            }
            if ((j | 0) == 16) {
                _abort();//fix cc 精简
            } else if ((j | 0) == 20) {
                b[f >> 1] = 4096;
                M = ((b[F >> 1] | 0) + 8192 + (b[E >> 1] << 15) | 0) >>> 14 & 65535;
                b[f + 2 >> 1] = M;
                b[a + 2 >> 1] = M;
                M = ((b[J + 4 >> 1] | 0) + 8192 + (b[I + 4 >> 1] << 15) | 0) >>> 14 & 65535;
                b[f + 4 >> 1] = M;
                b[a + 4 >> 1] = M;
                M = ((b[J + 6 >> 1] | 0) + 8192 + (b[I + 6 >> 1] << 15) | 0) >>> 14 & 65535;
                b[f + 6 >> 1] = M;
                b[a + 6 >> 1] = M;
                M = ((b[J + 8 >> 1] | 0) + 8192 + (b[I + 8 >> 1] << 15) | 0) >>> 14 & 65535;
                b[f + 8 >> 1] = M;
                b[a + 8 >> 1] = M;
                M = ((b[J + 10 >> 1] | 0) + 8192 + (b[I + 10 >> 1] << 15) | 0) >>> 14 & 65535;
                b[f + 10 >> 1] = M;
                b[a + 10 >> 1] = M;
                M = ((b[J + 12 >> 1] | 0) + 8192 + (b[I + 12 >> 1] << 15) | 0) >>> 14 & 65535;
                b[f + 12 >> 1] = M;
                b[a + 12 >> 1] = M;
                M = ((b[J + 14 >> 1] | 0) + 8192 + (b[I + 14 >> 1] << 15) | 0) >>> 14 & 65535;
                b[f + 14 >> 1] = M;
                b[a + 14 >> 1] = M;
                M = ((b[J + 16 >> 1] | 0) + 8192 + (b[I + 16 >> 1] << 15) | 0) >>> 14 & 65535;
                b[f + 16 >> 1] = M;
                b[a + 16 >> 1] = M;
                M = ((b[J + 18 >> 1] | 0) + 8192 + (b[I + 18 >> 1] << 15) | 0) >>> 14 & 65535;
                b[f + 18 >> 1] = M;
                b[a + 18 >> 1] = M;
                M = ((b[J + 20 >> 1] | 0) + 8192 + (b[I + 20 >> 1] << 15) | 0) >>> 14 & 65535;
                b[f + 20 >> 1] = M;
                b[a + 20 >> 1] = M;
                i = K;
                return 0
            }
            return 0
        }

        function Nc(a, c, d, e) {
            a = a | 0;
            c = c | 0;
            d = d | 0;
            e = e | 0;
            e = a >> 16;
            b[c >> 1] = e;
            b[d >> 1] = (a >>> 1) - (e << 15);
            return
        }

        function Oc(a) {
            a = a | 0;
            return ((a | 0) == -2147483648 ? 2147483647 : 0 - a | 0) | 0
        }

        function Pc(a) {
            a = a | 0;
            var b = 0;
            if (!a) {
                a = -1;
                return a | 0
            }
            c[a >> 2] = 0;
            b = Je(4) | 0;
            if (!b) {
                a = -1;
                return a | 0
            }
            c[b >> 2] = 0;
            if (!((Jc(b) | 0) << 16 >> 16)) {
                Kc(c[b >> 2] | 0) | 0;
                c[a >> 2] = b;
                a = 0;
                return a | 0
            } else {
                Lc(b);
                Ke(b);
                a = -1;
                return a | 0
            }
            return 0
        }

        function Qc(a) {
            a = a | 0;
            var b = 0;
            if (!a) return;
            b = c[a >> 2] | 0;
            if (!b) return;
            Lc(b);
            Ke(c[a >> 2] | 0);
            c[a >> 2] = 0;
            return
        }

        function Rc(a) {
            a = a | 0;
            if (!a) {
                a = -1;
                return a | 0
            }
            Kc(c[a >> 2] | 0) | 0;
            a = 0;
            return a | 0
        }

        function Sc(a, b, d, e, f, g, h) {
            a = a | 0;
            b = b | 0;
            d = d | 0;
            e = e | 0;
            f = f | 0;
            g = g | 0;
            h = h | 0;
            var j = 0, k = 0, l = 0, m = 0;
            m = i;
            i = i + 64 | 0;
            l = m + 48 | 0;
            k = m + 22 | 0;
            j = m;
            if ((b | 0) == 7) {
                d = c[g + 116 >> 2] | 0;
                Kb(e, 10, j, k, c[g + 112 >> 2] | 0, h) | 0;
                Hc(10, j, k, h);
                Mc(c[a >> 2] | 0, j, k, f + 22 | 0, l, h) | 0;
                Kb(e, 10, j, k, d, h) | 0;
                Hc(10, j, k, h);
                Mc(c[a >> 2] | 0, j, k, f + 66 | 0, l, h) | 0;
                i = m;
                return
            } else {
                Kb(d, 10, j, k, c[g + 108 >> 2] | 0, h) | 0;
                Hc(10, j, k, h);
                Mc(c[a >> 2] | 0, j, k, f + 66 | 0, l, h) | 0;
                i = m;
                return
            }
        }

        function Tc(a, c, d, e, f, g, h, i, j, k) {
            a = a | 0;
            c = c | 0;
            d = d | 0;
            e = e | 0;
            f = f | 0;
            g = g | 0;
            h = h | 0;
            i = i | 0;
            j = j | 0;
            k = k | 0;
            if ((d | 0) == 6) {
                b[f >> 1] = bd(a, c, e, 20, 143, 80, g, h, i, j, k) | 0;
                return
            }
            b[h >> 1] = 0;
            b[h + 2 >> 1] = 0;
            if (d >>> 0 < 2) {
                b[f >> 1] = Yc(c, d, e, 20, 143, 160, i, j, k) | 0;
                return
            }
            if (d >>> 0 < 6) {
                b[f >> 1] = Yc(c, d, e, 20, 143, 80, i, j, k) | 0;
                return
            } else {
                b[f >> 1] = Yc(c, d, e, 18, 143, 80, i, j, k) | 0;
                return
            }
        }

        function Uc(a) {
            a = a | 0;
            var d = 0;
            if ((a | 0) != 0 ? (c[a >> 2] = 0, d = Je(2) | 0, (d | 0) != 0) : 0) {
                b[d >> 1] = 0;
                c[a >> 2] = d;
                d = 0
            } else d = -1;
            return d | 0
        }

        function Vc(a) {
            a = a | 0;
            if (!a) a = -1; else {
                b[a >> 1] = 0;
                a = 0
            }
            return a | 0
        }

        function Wc(a) {
            a = a | 0;
            var b = 0;
            if (!a) return;
            b = c[a >> 2] | 0;
            if (!b) return;
            Ke(b);
            c[a >> 2] = 0;
            return
        }

        function Xc(a, c, d, f, g, h, j, k, l, m, n, o) {
            a = a | 0;
            c = c | 0;
            d = d | 0;
            f = f | 0;
            g = g | 0;
            h = h | 0;
            j = j | 0;
            k = k | 0;
            l = l | 0;
            m = m | 0;
            n = n | 0;
            o = o | 0;
            var p = 0, q = 0, r = 0, s = 0, t = 0, u = 0, v = 0, w = 0, x = 0, y = 0, z = 0, A = 0, B = 0, C = 0, D = 0,
                E = 0, F = 0, G = 0, H = 0, I = 0, J = 0, K = 0, L = 0, M = 0, N = 0, O = 0, P = 0, Q = 0, R = 0, S = 0,
                T = 0, U = 0;
            U = i;
            i = i + 240 | 0;
            u = U + 160 | 0;
            v = U + 80 | 0;
            O = U;
            N = b[3558 + (c * 18 | 0) >> 1] | 0;
            T = b[3558 + (c * 18 | 0) + 2 >> 1] | 0;
            p = b[3558 + (c * 18 | 0) + 4 >> 1] | 0;
            P = b[3558 + (c * 18 | 0) + 6 >> 1] | 0;
            s = b[3558 + (c * 18 | 0) + 12 >> 1] | 0;
            r = b[3558 + (c * 18 | 0) + 14 >> 1] | 0;
            q = b[3558 + (c * 18 | 0) + 16 >> 1] | 0;
            a:do switch (k << 16 >> 16) {
                case 0:
                case 80:
                    if (c >>> 0 < 2 & k << 16 >> 16 == 80) {
                        Q = (e[a >> 1] | 0) - (s & 65535) | 0;
                        Q = (Q << 16 >> 16 | 0) < (q << 16 >> 16 | 0) ? q : Q & 65535;
                        M = r << 16 >> 16;
                        R = (Q & 65535) + M & 65535;
                        S = R << 16 >> 16 > 143;
                        Q = S ? 143 - M & 65535 : Q;
                        R = S ? 143 : R;
                        S = 1;
                        break a
                    } else {
                        Q = (e[d + ((k << 16 >> 16 != 0 & 1) << 1) >> 1] | 0) - (e[3558 + (c * 18 | 0) + 8 >> 1] | 0) | 0;
                        Q = (Q << 16 >> 16 | 0) < (q << 16 >> 16 | 0) ? q : Q & 65535;
                        M = b[3558 + (c * 18 | 0) + 10 >> 1] | 0;
                        R = (Q & 65535) + M & 65535;
                        S = R << 16 >> 16 > 143;
                        Q = S ? 143 - M & 65535 : Q;
                        R = S ? 143 : R;
                        S = 0;
                        break a
                    }
                default: {
                    Q = (e[a >> 1] | 0) - (s & 65535) | 0;
                    Q = (Q << 16 >> 16 | 0) < (q << 16 >> 16 | 0) ? q : Q & 65535;
                    M = r << 16 >> 16;
                    R = (Q & 65535) + M & 65535;
                    S = R << 16 >> 16 > 143;
                    Q = S ? 143 - M & 65535 : Q;
                    R = S ? 143 : R;
                    S = 1
                }
            } while (0);
            L = Q & 65535;
            k = L + 65532 | 0;
            t = k & 65535;
            K = (R & 65535) + 4 & 65535;
            M = k << 16 >> 16;
            k = 0 - (k & 65535) | 0;
            s = k & 65535;
            ec(f + (k << 16 >> 16 << 1) | 0, h, u, j);
            k = j << 16 >> 16;
            B = k >>> 1 & 65535;
            w = B << 16 >> 16 == 0;
            if (w) j = 1; else {
                j = B;
                q = u;
                d = v;
                r = 0;
                while (1) {
                    J = b[q >> 1] | 0;
                    b[d >> 1] = J >>> 2;
                    J = (Z(J, J) | 0) + r | 0;
                    r = b[q + 2 >> 1] | 0;
                    b[d + 2 >> 1] = r >>> 2;
                    r = J + (Z(r, r) | 0) | 0;
                    j = j + -1 << 16 >> 16;
                    if (!(j << 16 >> 16)) break; else {
                        q = q + 4 | 0;
                        d = d + 4 | 0
                    }
                }
                j = (r | 0) < 33554433
            }
            J = j ? 0 : 2;
            A = j ? u : v;
            x = j ? u : v;
            b:do if (t << 16 >> 16 <= K << 16 >> 16) {
                y = k + -1 | 0;
                G = A + (y << 1) | 0;
                H = h + (y << 1) | 0;
                I = A + (k + -2 << 1) | 0;
                D = y >>> 1;
                E = D & 65535;
                z = E << 16 >> 16 == 0;
                F = j ? 12 : 14;
                D = (D << 1) + 131070 & 131070;
                d = k + -3 - D | 0;
                C = A + (d << 1) | 0;
                D = A + (k + -4 - D << 1) | 0;
                h = h + (d << 1) | 0;
                if (!w) {
                    w = M;
                    while (1) {
                        v = B;
                        u = x;
                        q = g;
                        r = 0;
                        j = 0;
                        while (1) {
                            v = v + -1 << 16 >> 16;
                            k = b[u >> 1] | 0;
                            r = (Z(k, b[q >> 1] | 0) | 0) + r | 0;
                            k = (Z(k, k) | 0) + j | 0;
                            j = b[u + 2 >> 1] | 0;
                            r = r + (Z(j, b[q + 2 >> 1] | 0) | 0) | 0;
                            j = k + (Z(j, j) | 0) | 0;
                            if (!(v << 16 >> 16)) break; else {
                                u = u + 4 | 0;
                                q = q + 4 | 0
                            }
                        }
                        u = ce(j << 1, o) | 0;
                        j = u >> 16;
                        q = r << 1 >> 16;
                        v = Z(j, q) | 0;
                        v = (v | 0) == 1073741824 ? 2147483647 : v << 1;
                        q = (Z((u >>> 1) - (j << 15) << 16 >> 16, q) | 0) >> 15;
                        u = (q << 1) + v | 0;
                        u = (q ^ v | 0) > 0 & (u ^ v | 0) < 0 ? (v >>> 31) + 2147483647 | 0 : u;
                        j = (Z(j, r & 32767) | 0) >> 15;
                        v = u + (j << 1) | 0;
                        b[O + (w - M << 1) >> 1] = (u ^ j | 0) > 0 & (v ^ u | 0) < 0 ? (u >>> 31) + 65535 | 0 : v;
                        if (t << 16 >> 16 != K << 16 >> 16) {
                            s = s + -1 << 16 >> 16;
                            v = b[f + (s << 16 >> 16 << 1) >> 1] | 0;
                            if (z) {
                                u = y;
                                j = I;
                                r = H;
                                q = G
                            } else {
                                u = E;
                                j = I;
                                r = H;
                                q = G;
                                while (1) {
                                    w = (Z(b[r >> 1] | 0, v) | 0) >> F;
                                    b[q >> 1] = w + (e[j >> 1] | 0);
                                    w = (Z(b[r + -2 >> 1] | 0, v) | 0) >> F;
                                    b[q + -2 >> 1] = w + (e[j + -2 >> 1] | 0);
                                    u = u + -1 << 16 >> 16;
                                    if (!(u << 16 >> 16)) {
                                        u = d;
                                        j = D;
                                        r = h;
                                        q = C;
                                        break
                                    } else {
                                        j = j + -4 | 0;
                                        r = r + -4 | 0;
                                        q = q + -4 | 0
                                    }
                                }
                            }
                            w = (Z(b[r >> 1] | 0, v) | 0) >> F;
                            b[q >> 1] = w + (e[j >> 1] | 0);
                            b[A + (u + -1 << 1) >> 1] = v >> J
                        }
                        t = t + 1 << 16 >> 16;
                        if (t << 16 >> 16 > K << 16 >> 16) break b; else w = t << 16 >> 16
                    }
                }
                if (z) {
                    _abort();//fix cc 精简
                }
                u = A + (d + -1 << 1) | 0;
                j = M;
                while (1) {
                    ce(0, o) | 0;
                    b[O + (j - M << 1) >> 1] = 0;
                    if (t << 16 >> 16 != K << 16 >> 16) {
                        _abort();//fix cc 精简
                    }
                    t = t + 1 << 16 >> 16;
                    if (t << 16 >> 16 > K << 16 >> 16) break; else j = t << 16 >> 16
                }
            } while (0);
            t = Q << 16 >> 16;
            d = L + 1 & 65535;
            if (d << 16 >> 16 > R << 16 >> 16) h = Q; else {
                s = Q;
                k = b[O + (t - M << 1) >> 1] | 0;
                while (1) {
                    r = b[O + ((d << 16 >> 16) - M << 1) >> 1] | 0;
                    q = r << 16 >> 16 < k << 16 >> 16;
                    s = q ? s : d;
                    d = d + 1 << 16 >> 16;
                    if (d << 16 >> 16 > R << 16 >> 16) {
                        h = s;
                        break
                    } else k = q ? k : r
                }
            }
            c:do if (!(S << 16 >> 16 == 0 ? h << 16 >> 16 > N << 16 >> 16 : 0)) {
                if (!(c >>> 0 < 4 & S << 16 >> 16 != 0)) {
                    s = O + ((h << 16 >> 16) - M << 1) | 0;
                    r = Fc(s, p, T, o) | 0;
                    d = (p & 65535) + 1 & 65535;
                    if (d << 16 >> 16 <= P << 16 >> 16) while (1) {
                        q = Fc(s, d, T, o) | 0;
                        k = q << 16 >> 16 > r << 16 >> 16;
                        p = k ? d : p;
                        d = d + 1 << 16 >> 16;
                        if (d << 16 >> 16 > P << 16 >> 16) break; else r = k ? q : r
                    }
                    if ((c + -7 | 0) >>> 0 < 2) {
                        P = p << 16 >> 16 == -3;
                        d = (P << 31 >> 31) + h << 16 >> 16;
                        p = P ? 3 : p;
                        break
                    }
                    switch (p << 16 >> 16) {
                        case -2: {
                            d = h + -1 << 16 >> 16;
                            p = 1;
                            break c
                        }
                        case 2: {
                            d = h + 1 << 16 >> 16;
                            p = -1;
                            break c
                        }
                        default: {
                            d = h;
                            break c
                        }
                    }
                }
                N = b[a >> 1] | 0;
                N = ((N << 16 >> 16) - t | 0) > 5 ? t + 5 & 65535 : N;
                k = R << 16 >> 16;
                N = (k - (N << 16 >> 16) | 0) > 4 ? k + 65532 & 65535 : N;
                k = h << 16 >> 16;
                d = N << 16 >> 16;
                if ((k | 0) == (d + -1 | 0) ? 1 : h << 16 >> 16 == N << 16 >> 16) {
                    s = O + (k - M << 1) | 0;
                    k = Fc(s, p, T, o) | 0;
                    d = (p & 65535) + 1 & 65535;
                    if (d << 16 >> 16 <= P << 16 >> 16) while (1) {
                        r = Fc(s, d, T, o) | 0;
                        q = r << 16 >> 16 > k << 16 >> 16;
                        p = q ? d : p;
                        d = d + 1 << 16 >> 16;
                        if (d << 16 >> 16 > P << 16 >> 16) break; else k = q ? r : k
                    }
                    if ((c + -7 | 0) >>> 0 < 2) {
                        _abort();//fix cc 精简
                    }
                    switch (p << 16 >> 16) {
                        case -2: {
                            d = h + -1 << 16 >> 16;
                            p = 1;
                            break c
                        }
                        case 2: {
                            d = h + 1 << 16 >> 16;
                            p = -1;
                            break c
                        }
                        default: {
                            d = h;
                            break c
                        }
                    }
                }
                if ((k | 0) == (d + -2 | 0)) {
                    d = O + (k - M << 1) | 0;
                    k = Fc(d, 0, T, o) | 0;
                    if ((c | 0) != 8) {
                        p = 0;
                        s = 1;
                        while (1) {
                            r = Fc(d, s, T, o) | 0;
                            q = r << 16 >> 16 > k << 16 >> 16;
                            p = q ? s : p;
                            s = s + 1 << 16 >> 16;
                            if (s << 16 >> 16 > P << 16 >> 16) break; else k = q ? r : k
                        }
                        if ((c + -7 | 0) >>> 0 >= 2) switch (p << 16 >> 16) {
                            case -2: {
                                d = h + -1 << 16 >> 16;
                                p = 1;
                                break c
                            }
                            case 2: {
                                d = h + 1 << 16 >> 16;
                                p = -1;
                                break c
                            }
                            default: {
                                d = h;
                                break c
                            }
                        }
                    } else p = 0;
                    P = p << 16 >> 16 == -3;
                    d = (P << 31 >> 31) + h << 16 >> 16;
                    p = P ? 3 : p;
                    break
                }
                if ((k | 0) == (d + 1 | 0)) {
                    s = O + (k - M << 1) | 0;
                    d = Fc(s, p, T, o) | 0;
                    k = (p & 65535) + 1 & 65535;
                    if (k << 16 >> 16 <= 0) while (1) {
                        q = Fc(s, k, T, o) | 0;
                        r = q << 16 >> 16 > d << 16 >> 16;
                        p = r ? k : p;
                        k = k + 1 << 16 >> 16;
                        if (k << 16 >> 16 > 0) break; else d = r ? q : d
                    }
                    if ((c + -7 | 0) >>> 0 < 2) {
                        _abort();//fix cc 精简
                    }
                    switch (p << 16 >> 16) {
                        case -2: {
                            d = h + -1 << 16 >> 16;
                            p = 1;
                            break c
                        }
                        case 2: {
                            d = h + 1 << 16 >> 16;
                            p = -1;
                            break c
                        }
                        default: {
                            d = h;
                            break c
                        }
                    }
                } else {
                    d = h;
                    p = 0
                }
            } else {
                d = h;
                p = 0
            } while (0);
            if ((c + -7 | 0) >>> 0 > 1) {
                P = a;
                a = pc(d, p, b[a >> 1] | 0, Q, R, S, c >>> 0 < 4 & 1, o) | 0;
                b[n >> 1] = a;
                b[P >> 1] = d;
                b[m >> 1] = T;
                b[l >> 1] = p;
                i = U;
                return d | 0
            } else {
                o = qc(d, p, Q, S, o) | 0;
                b[n >> 1] = o;
                b[a >> 1] = d;
                b[m >> 1] = T;
                b[l >> 1] = p;
                i = U;
                return d | 0
            }
            return 0
        }

        function Yc(a, d, e, f, g, h, j, k, l) {
            a = a | 0;
            d = d | 0;
            e = e | 0;
            f = f | 0;
            g = g | 0;
            h = h | 0;
            j = j | 0;
            k = k | 0;
            l = l | 0;
            var m = 0, n = 0, o = 0, p = 0, q = 0, r = 0, s = 0, t = 0, u = 0, v = 0, w = 0, x = 0, y = 0, z = 0, A = 0,
                B = 0, C = 0, D = 0;
            D = i;
            i = i + 1200 | 0;
            B = D + 1188 | 0;
            A = D + 580 | 0;
            C = D + 578 | 0;
            z = D + 576 | 0;
            v = D;
            x = D + 582 | 0;
            y = (k | 0) != 0;
            if (y) {
				_abort();//fix cc 精简
			}
            w = g << 16 >> 16;
            o = 0 - w | 0;
            n = e + (o << 1) | 0;
            o = o & 65535;
            s = h << 16 >> 16;
            do if (o << 16 >> 16 < h << 16 >> 16) {
                r = o;
                q = n;
                o = 0;
                while (1) {
                    t = b[q >> 1] | 0;
                    o = (Z(t << 1, t) | 0) + o | 0;
                    if ((o | 0) < 0) break;
                    r = r + 1 << 16 >> 16;
                    if (r << 16 >> 16 >= h << 16 >> 16) {
                        u = 14;
                        break
                    } else q = q + 2 | 0
                }
                if ((u | 0) == 14) {
                    if ((o | 0) < 1048576) {
                        u = 15;
                        break
                    }
                    Oe(x | 0, n | 0, s + w << 1 | 0) | 0;
                    t = 0;
                    break
                }
                m = s + w | 0;
                p = m >>> 1;
                r = p & 65535;
                if (!(r << 16 >> 16)) o = x; else {
                    t = ((p << 1) + 131070 & 131070) + 2 | 0;
                    s = t - w | 0;
                    q = x;
                    while (1) {
                        b[q >> 1] = (b[n >> 1] | 0) >>> 3;
                        b[q + 2 >> 1] = (b[n + 2 >> 1] | 0) >>> 3;
                        r = r + -1 << 16 >> 16;
                        if (!(r << 16 >> 16)) break; else {
                            n = n + 4 | 0;
                            q = q + 4 | 0
                        }
                    }
                    n = e + (s << 1) | 0;
                    o = x + (t << 1) | 0
                }
                if (!(m & 1)) t = 3; else {
                    b[o >> 1] = (b[n >> 1] | 0) >>> 3;
                    t = 3
                }
            } else u = 15; while (0);
            if ((u | 0) == 15) {
                t = s + w | 0;
                o = t >>> 1;
                p = o & 65535;
                if (!(p << 16 >> 16)) o = x; else {
                    s = ((o << 1) + 131070 & 131070) + 2 | 0;
                    q = s - w | 0;
                    r = x;
                    while (1) {
                        b[r >> 1] = b[n >> 1] << 3;
                        b[r + 2 >> 1] = b[n + 2 >> 1] << 3;
                        p = p + -1 << 16 >> 16;
                        if (!(p << 16 >> 16)) break; else {
                            n = n + 4 | 0;
                            r = r + 4 | 0
                        }
                    }
                    n = e + (q << 1) | 0;
                    o = x + (s << 1) | 0
                }
                if (!(t & 1)) t = -3; else {
                    b[o >> 1] = b[n >> 1] << 3;
                    t = -3
                }
            }
            s = v + (w << 2) | 0;
            q = x + (w << 1) | 0;
            Tb(q, h, g, f, s);
            m = (d | 0) == 7 & 1;
            o = f << 16 >> 16;
            n = o << 2;
            if ((n | 0) != (o << 18 >> 16 | 0)) {
                c[l >> 2] = 1;
                n = f << 16 >> 16 > 0 ? 32767 : -32768
            }
            r = Zc(a, s, q, t, m, h, g, n & 65535, B, k, l) | 0;
            o = o << 1;
            p = Zc(a, s, q, t, m, h, n + 65535 & 65535, o & 65535, A, k, l) | 0;
            o = Zc(a, s, q, t, m, h, o + 65535 & 65535, f, C, k, l) | 0;
            if (j << 16 >> 16 == 1 & y) {
                _abort();//fix cc 精简
                
            }
            n = b[B >> 1] | 0;
            m = b[A >> 1] | 0;
            if (((n << 16 >> 16) * 55706 >> 16 | 0) >= (m << 16 >> 16 | 0)) {
                A = n;
                B = r;
                A = A << 16 >> 16;
                A = A * 55706 | 0;
                A = A >> 16;
                C = b[C >> 1] | 0;
                C = C << 16 >> 16;
                C = (A | 0) < (C | 0);
                C = C ? o : B;
                i = D;
                return C | 0
            }
            b[B >> 1] = m;
            A = m;
            B = p;
            A = A << 16 >> 16;
            A = A * 55706 | 0;
            A = A >> 16;
            C = b[C >> 1] | 0;
            C = C << 16 >> 16;
            C = (A | 0) < (C | 0);
            C = C ? o : B;
            i = D;
            return C | 0
        }

        function Zc(a, d, e, f, g, h, i, j, k, l, m) {
            a = a | 0;
            d = d | 0;
            e = e | 0;
            f = f | 0;
            g = g | 0;
            h = h | 0;
            i = i | 0;
            j = j | 0;
            k = k | 0;
            l = l | 0;
            m = m | 0;
            var n = 0, o = 0, p = 0, q = 0, r = 0;
            if (i << 16 >> 16 < j << 16 >> 16) {
                j = -2147483648;
                p = i
            } else {
                p = i;
                n = -2147483648;
                o = d + (0 - (i << 16 >> 16) << 2) | 0;
                d = i;
                while (1) {
                    i = c[o >> 2] | 0;
                    r = (i | 0) < (n | 0);
                    d = r ? d : p;
                    n = r ? n : i;
                    p = p + -1 << 16 >> 16;
                    if (p << 16 >> 16 < j << 16 >> 16) {
                        j = n;
                        p = d;
                        break
                    } else o = o + 4 | 0
                }
            }
            d = h << 16 >> 16 >>> 2 & 65535;
            if (!(d << 16 >> 16)) d = 0; else {
                n = d;
                i = e + (0 - (p << 16 >> 16) << 1) | 0;
                d = 0;
                while (1) {
                    r = b[i >> 1] | 0;
                    r = (Z(r, r) | 0) + d | 0;
                    d = b[i + 2 >> 1] | 0;
                    d = r + (Z(d, d) | 0) | 0;
                    r = b[i + 4 >> 1] | 0;
                    r = d + (Z(r, r) | 0) | 0;
                    d = b[i + 6 >> 1] | 0;
                    d = r + (Z(d, d) | 0) | 0;
                    n = n + -1 << 16 >> 16;
                    if (!(n << 16 >> 16)) break; else i = i + 8 | 0
                }
                d = d << 1
            }
            if (l) _abort();//fix cc 精简
            d = ce(d, m) | 0;
            i = g << 16 >> 16 != 0;
            if (i) d = (d | 0) > 1073741823 ? 2147483647 : d << 1;
            g = j >> 16;
            a = d >> 16;
            m = Z(a, g) | 0;
            m = (m | 0) == 1073741824 ? 2147483647 : m << 1;
            d = (Z((d >>> 1) - (a << 15) << 16 >> 16, g) | 0) >> 15;
            r = (d << 1) + m | 0;
            r = (d ^ m | 0) > 0 & (r ^ m | 0) < 0 ? (m >>> 31) + 2147483647 | 0 : r;
            g = (Z(a, (j >>> 1) - (g << 15) << 16 >> 16) | 0) >> 15;
            d = r + (g << 1) | 0;
            d = (r ^ g | 0) > 0 & (d ^ r | 0) < 0 ? (r >>> 31) + 2147483647 | 0 : d;
            if (!i) {
                b[k >> 1] = d;
                return p | 0
            }
            i = f << 16 >> 16;
            if (f << 16 >> 16 > 0) if (f << 16 >> 16 < 31) {
                i = d >> i;
                q = 16
            } else i = 0; else {
                q = 0 - i << 16 >> 16;
                i = d << q;
                i = (i >> q | 0) == (d | 0) ? i : d >> 31 ^ 2147483647;
                q = 16
            }
            if ((q | 0) == 16) {
                if ((i | 0) > 65535) {
                    b[k >> 1] = 32767;
                    return p | 0
                }
                if ((i | 0) < -65536) {
                    b[k >> 1] = -32768;
                    return p | 0
                }
            }
            b[k >> 1] = i >>> 1;
            return p | 0
        }

        function _c(a) {
            a = a | 0;
            var d = 0;
            if (!a) {
                a = -1;
                return a | 0
            }
            c[a >> 2] = 0;
            d = Je(6) | 0;
            if (!d) {
                a = -1;
                return a | 0
            }
            b[d >> 1] = 40;
            b[d + 2 >> 1] = 0;
            b[d + 4 >> 1] = 0;
            c[a >> 2] = d;
            a = 0;
            return a | 0
        }

        function $c(a) {
            a = a | 0;
            if (!a) {
                a = -1;
                return a | 0
            }
            b[a >> 1] = 40;
            b[a + 2 >> 1] = 0;
            b[a + 4 >> 1] = 0;
            a = 0;
            return a | 0
        }

        function ad(a) {
            a = a | 0;
            var b = 0;
            if (!a) return;
            b = c[a >> 2] | 0;
            if (!b) return;
            Ke(b);
            c[a >> 2] = 0;
            return
        }

        function bd(a, d, e, f, g, h, j, k, l, m, n) {
            a = a | 0;
            d = d | 0;
            e = e | 0;
            f = f | 0;
            g = g | 0;
            h = h | 0;
            j = j | 0;
            k = k | 0;
            l = l | 0;
            m = m | 0;
            n = n | 0;
            var o = 0, p = 0, q = 0, r = 0, s = 0, t = 0, u = 0, v = 0, w = 0, x = 0, y = 0, z = 0, A = 0, B = 0, C = 0,
                D = 0, E = 0, F = 0;
            F = i;
            i = i + 1200 | 0;
            w = F + 1186 | 0;
            x = F + 1184 | 0;
            E = F + 1182 | 0;
            v = F;
            z = F + 576 | 0;
            y = g << 16 >> 16;
            D = z + (y << 1) | 0;
            o = (0 - y & 65535) << 16 >> 16 < h << 16 >> 16;
            if (o) {
                s = 0 - g << 16 >> 16 << 16 >> 16;
                p = 0;
                do {
                    r = b[e + (s << 1) >> 1] | 0;
                    r = Z(r, r) | 0;
                    if ((r | 0) != 1073741824) {
                        q = (r << 1) + p | 0;
                        if ((r ^ p | 0) > 0 & (q ^ p | 0) < 0) {
                            c[n >> 2] = 1;
                            p = (p >>> 31) + 2147483647 | 0
                        } else p = q
                    } else {
                        c[n >> 2] = 1;
                        p = 2147483647
                    }
                    s = s + 1 | 0
                } while ((s & 65535) << 16 >> 16 != h << 16 >> 16)
            } else p = 0;
            if ((2147483646 - p & p | 0) >= 0) if ((p | 0) == 2147483647) {
                if (o) {
                    p = 0 - g << 16 >> 16 << 16 >> 16;
                    do {
                        b[z + (p + y << 1) >> 1] = De(b[e + (p << 1) >> 1] | 0, 3, n) | 0;
                        p = p + 1 | 0
                    } while ((p & 65535) << 16 >> 16 != h << 16 >> 16)
                }
            } else t = 14; else {
                c[n >> 2] = 1;
                t = 14
            }
            do if ((t | 0) == 14) {
                if ((1048575 - p & p | 0) < 0) {
                    c[n >> 2] = 1;
                    p = (p >>> 31) + 2147483647 | 0
                } else p = p + -1048576 | 0;
                if ((p | 0) >= 0) {
                    if (!o) break;
                    C = 0 - g << 16 >> 16 << 16 >> 16;
                    Oe(z + (y + C << 1) | 0, e + (C << 1) | 0, (((h + g << 16 >> 16) + -1 & 65535) << 1) + 2 | 0) | 0;
                    break
                }
                if (o) {//不可精简
                    p = 0 - g << 16 >> 16 << 16 >> 16;
                    do {
                        C = b[e + (p << 1) >> 1] | 0;
                        b[z + (p + y << 1) >> 1] = (C << 19 >> 19 | 0) == (C | 0) ? C << 3 : C >>> 15 ^ 32767;
                        p = p + 1 | 0
                    } while ((p & 65535) << 16 >> 16 != h << 16 >> 16)
                }
            } while (0);
            B = v + (y << 2) | 0;
            Tb(D, h, g, f, B);
            s = b[a >> 1] | 0;
            C = a + 4 | 0;
            A = k + (l << 16 >> 16 << 1) | 0;
            a:do if (g << 16 >> 16 < f << 16 >> 16) u = g; else {
                if ((b[C >> 1] | 0) <= 0) {
                    e = g;
                    k = -2147483648;
                    r = g;
                    t = 3402;
                    while (1) {
                        Nc(c[v + (y - (e << 16 >> 16) << 2) >> 2] | 0, w, x, n);
                        q = b[x >> 1] | 0;
                        p = b[t >> 1] | 0;
                        s = Z(p, b[w >> 1] | 0) | 0;
                        if ((s | 0) == 1073741824) {
                            c[n >> 2] = 1;
                            o = 2147483647
                        } else o = s << 1;
                        u = (Z(p, q << 16 >> 16) | 0) >> 15;
                        s = o + (u << 1) | 0;
                        if ((o ^ u | 0) > 0 & (s ^ o | 0) < 0) {
                            _abort();//fix cc 精简
                        }
                        q = (s | 0) < (k | 0);
                        r = q ? r : e;
                        e = e + -1 << 16 >> 16;
                        if (e << 16 >> 16 < f << 16 >> 16) {
                            u = r;
                            break a
                        } else {
                            k = q ? k : s;
                            t = t + -2 | 0
                        }
                    }
                }
                k = g;
                o = -2147483648;
                r = g;
                u = 2902 + (y + 123 - (s << 16 >> 16) << 1) | 0;
                e = 3402;
                while (1) {
                    Nc(c[v + (y - (k << 16 >> 16) << 2) >> 2] | 0, w, x, n);
                    t = b[x >> 1] | 0;
                    q = b[e >> 1] | 0;
                    s = Z(q, b[w >> 1] | 0) | 0;
                    if ((s | 0) == 1073741824) {
                        c[n >> 2] = 1;
                        p = 2147483647
                    } else p = s << 1;
                    t = (Z(q, t << 16 >> 16) | 0) >> 15;
                    s = p + (t << 1) | 0;
                    if ((p ^ t | 0) > 0 & (s ^ p | 0) < 0) {
                        c[n >> 2] = 1;
                        s = (p >>> 31) + 2147483647 | 0
                    }
                    Nc(s, w, x, n);
                    t = b[x >> 1] | 0;
                    q = b[u >> 1] | 0;
                    s = Z(q, b[w >> 1] | 0) | 0;
                    if ((s | 0) == 1073741824) {
                        c[n >> 2] = 1;
                        p = 2147483647
                    } else p = s << 1;
                    t = (Z(q, t << 16 >> 16) | 0) >> 15;
                    s = p + (t << 1) | 0;
                    if ((p ^ t | 0) > 0 & (s ^ p | 0) < 0) {
                        c[n >> 2] = 1;
                        s = (p >>> 31) + 2147483647 | 0
                    }
                    q = (s | 0) < (o | 0);
                    r = q ? r : k;
                    k = k + -1 << 16 >> 16;
                    if (k << 16 >> 16 < f << 16 >> 16) {
                        u = r;
                        break
                    } else {
                        o = q ? o : s;
                        u = u + -2 | 0;
                        e = e + -2 | 0
                    }
                }
            } while (0);
            if (h << 16 >> 16 > 0) {
                k = 0;
                e = D;
                t = z + (y - (u << 16 >> 16) << 1) | 0;
                r = 0;
                p = 0;
                while (1) {
                    s = b[t >> 1] | 0;
                    q = Z(s, b[e >> 1] | 0) | 0;
                    if ((q | 0) != 1073741824) {
                        o = (q << 1) + r | 0;
                        if ((q ^ r | 0) > 0 & (o ^ r | 0) < 0) {
                            _abort();//fix cc 精简
                        } else r = o
                    } else {
                        c[n >> 2] = 1;
                        r = 2147483647
                    }
                    o = Z(s, s) | 0;
                    if ((o | 0) != 1073741824) {
                        q = (o << 1) + p | 0;
                        if ((o ^ p | 0) > 0 & (q ^ p | 0) < 0) {
                            _abort();//fix cc 精简
                        } else p = q
                    } else {
                        c[n >> 2] = 1;
                        p = 2147483647
                    }
                    k = k + 1 << 16 >> 16;
                    if (k << 16 >> 16 >= h << 16 >> 16) break; else {
                        e = e + 2 | 0;
                        t = t + 2 | 0
                    }
                }
            } else {
                r = 0;
                p = 0
            }
            q = (m | 0) == 0;
            if (!q) {
                _abort();//fix cc 精简
                
            }
            o = (Ce(p, n) | 0) << 16 >> 16;
            if ((o * 13107 | 0) == 1073741824) {
                c[n >> 2] = 1;
                p = 2147483647
            } else p = o * 26214 | 0;
            o = r - p | 0;
            if (((o ^ r) & (p ^ r) | 0) < 0) {
                c[n >> 2] = 1;
                o = (r >>> 31) + 2147483647 | 0
            }
            m = Ce(o, n) | 0;
            b[A >> 1] = m;
            if (m << 16 >> 16 > 0) {
                o = j + 6 | 0;
                b[j + 8 >> 1] = b[o >> 1] | 0;
                m = j + 4 | 0;
                b[o >> 1] = b[m >> 1] | 0;
                o = j + 2 | 0;
                b[m >> 1] = b[o >> 1] | 0;
                b[o >> 1] = b[j >> 1] | 0;
                b[j >> 1] = u;
                b[a >> 1] = Zd(j, 5) | 0;
                b[a + 2 >> 1] = 32767;
                o = 32767
            } else {
                b[a >> 1] = u;
                a = a + 2 | 0;
                o = ((b[a >> 1] | 0) * 29491 | 0) >>> 15 & 65535;
                b[a >> 1] = o
            }
            b[C >> 1] = ((Ge(o, 9830, n) | 0) & 65535) >>> 15 ^ 1;
            if (q) {
                i = F;
                return u | 0
            }
            if ((Ge(l, 1, n) | 0) << 16 >> 16) {
                i = F;
                return u | 0
            }
            _abort();//fix cc 精简
			
			
            return u | 0
        }

        function cd(a, b, c, d, e, f, g, h, j, k) {
            a = a | 0;
            b = b | 0;
            c = c | 0;
            d = d | 0;
            e = e | 0;
            f = f | 0;
            g = g | 0;
            h = h | 0;
            j = j | 0;
            k = k | 0;
            var l = 0, m = 0;
            k = i;
            i = i + 48 | 0;
            m = k + 22 | 0;
            l = k;
            b = a >>> 0 < 6 ? b : c;
            c = f << 16 >> 16 > 0 ? 22 : 0;
            a = e + (c << 1) | 0;
            Ie(a, b, m);
            Ie(a, d, l);
            a = f << 16 >> 16;
            f = j + (a << 1) | 0;
            Be(m, g + (a << 1) | 0, f, 40);
            He(l, f, f, 40, h, 1);
            c = e + (((c << 16) + 720896 | 0) >>> 16 << 1) | 0;
            Ie(c, b, m);
            Ie(c, d, l);
            a = (a << 16) + 2621440 >> 16;
            j = j + (a << 1) | 0;
            Be(m, g + (a << 1) | 0, j, 40);
            He(l, j, j, 40, h, 1);
            i = k;
            return
        }

        function dd(a) {
            a = a | 0;
            var d = 0;
            if (!a) {
                a = -1;
                return a | 0
            }
            c[a >> 2] = 0;
            d = Je(12) | 0;
            if (!d) {
                a = -1;
                return a | 0
            }
            ;b[d >> 1] = 0;
            b[d + 2 >> 1] = 0;
            b[d + 4 >> 1] = 0;
            b[d + 6 >> 1] = 0;
            b[d + 8 >> 1] = 0;
            b[d + 10 >> 1] = 0;
            c[a >> 2] = d;
            a = 0;
            return a | 0
        }

        function ed(a) {
            a = a | 0;
            if (!a) {
                a = -1;
                return a | 0
            }
            ;b[a >> 1] = 0;
            b[a + 2 >> 1] = 0;
            b[a + 4 >> 1] = 0;
            b[a + 6 >> 1] = 0;
            b[a + 8 >> 1] = 0;
            b[a + 10 >> 1] = 0;
            a = 0;
            return a | 0
        }

        function fd(a) {
            a = a | 0;
            var b = 0;
            if (!a) return;
            b = c[a >> 2] | 0;
            if (!b) return;
            Ke(b);
            c[a >> 2] = 0;
            return
        }

        function gd(a, c, d) {
            a = a | 0;
            c = c | 0;
            d = d | 0;
            var e = 0, f = 0, g = 0, h = 0, i = 0, j = 0, k = 0, l = 0, m = 0, n = 0, o = 0;
            m = a + 10 | 0;
            f = b[m >> 1] | 0;
            n = a + 8 | 0;
            e = b[n >> 1] | 0;
            if (!(d << 16 >> 16)) {
                _abort();//fix cc 精简
            }
            i = a + 4 | 0;
            j = a + 6 | 0;
            k = a + 2 | 0;
            h = b[j >> 1] | 0;
            l = b[i >> 1] | 0;
            g = d;
            d = f;
            while (1) {
                o = (Z(b[a >> 1] | 0, -3733) | 0) + (((l << 16 >> 16) * 7807 | 0) + ((h << 16 >> 16) * 7807 >> 15)) | 0;
                b[a >> 1] = l;
                o = o + ((Z(b[k >> 1] | 0, -3733) | 0) >> 15) | 0;
                b[k >> 1] = h;
                o = ((d << 16 >> 16) * 1899 | 0) + o + (Z(e << 16 >> 16, -3798) | 0) | 0;
                d = b[c >> 1] | 0;
                o = o + ((d << 16 >> 16) * 1899 | 0) | 0;
                b[c >> 1] = (o + 2048 | 0) >>> 12;
                f = o >>> 12;
                l = f & 65535;
                b[i >> 1] = l;
                h = (o << 3) - (f << 15) & 65535;
                b[j >> 1] = h;
                g = g + -1 << 16 >> 16;
                if (!(g << 16 >> 16)) break; else {
                    o = e;
                    c = c + 2 | 0;
                    e = d;
                    d = o
                }
            }
            b[m >> 1] = e;
            b[n >> 1] = d;
            return
        }

        function hd(a, d, e, f) {
            a = a | 0;
            d = d | 0;
            e = e | 0;
            f = f | 0;
            var g = 0, h = 0, i = 0, j = 0;
            g = b[(c[f + 88 >> 2] | 0) + (a << 1) >> 1] | 0;
            if (!(g << 16 >> 16)) return;
            j = e;
            i = c[(c[f + 92 >> 2] | 0) + (a << 2) >> 2] | 0;
            while (1) {
                e = b[i >> 1] | 0;
                if (!(e << 16 >> 16)) e = 0; else {
                    a = b[d >> 1] | 0;
                    h = e;
                    f = j + ((e << 16 >> 16) + -1 << 1) | 0;
                    while (1) {
                        e = a << 16 >> 16;
                        b[f >> 1] = e & 1;
                        h = h + -1 << 16 >> 16;
                        if (!(h << 16 >> 16)) break; else {
                            a = e >>> 1 & 65535;
                            f = f + -2 | 0
                        }
                    }
                    e = b[i >> 1] | 0
                }
                d = d + 2 | 0;
                g = g + -1 << 16 >> 16;
                if (!(g << 16 >> 16)) break; else {
                    j = j + (e << 16 >> 16 << 1) | 0;
                    i = i + 2 | 0
                }
            }
            return
        }

        function id(a, d, f, g, h, j) {
            a = a | 0;
            d = d | 0;
            f = f | 0;
            g = g | 0;
            h = h | 0;
            j = j | 0;
            var k = 0, l = 0, m = 0, n = 0, o = 0;
            o = i;
            i = i + 16 | 0;
            m = o + 2 | 0;
            n = o;
            k = h << 16 >> 16;
            if (h << 16 >> 16 < 1) {
                j = -5443;
                n = -32768;
                Wd(a, n, j);
                i = o;
                return
            }
            l = re(14, f, j) | 0;
            if ((k | 0) < (l << 16 >> 16 | 0)) f = g; else {
                f = (g & 65535) + 1 & 65535;
                h = k >>> 1 & 65535
            }
            g = Td(h, l & 65535) | 0;
            b[n >> 1] = g;
            de(g << 16 >> 16, m, n, j);
            b[m >> 1] = ((((f & 65535) - (d & 65535) << 16) + -65536 | 0) >>> 16) + (e[m >> 1] | 0);
            g = Ee(b[n >> 1] | 0, 5, j) | 0;
            k = b[m >> 1] | 0;
            g = ((k & 65535) << 10) + (g & 65535) & 65535;
            if (g << 16 >> 16 > 18284) {
                _abort();//fix cc 精简
            }
            h = b[n >> 1] | 0;
            k = k << 16 >> 16;
            if ((k * 24660 | 0) == 1073741824) {
                c[j >> 2] = 1;
                f = 2147483647
            } else f = k * 49320 | 0;
            n = (h << 16 >> 16) * 24660 >> 15;
            k = f + (n << 1) | 0;
            if ((f ^ n | 0) > 0 & (k ^ f | 0) < 0) {
                c[j >> 2] = 1;
                k = (f >>> 31) + 2147483647 | 0
            }
            n = k << 13;
            j = Ce((n >> 13 | 0) == (k | 0) ? n : k >> 31 ^ 2147483647, j) | 0;
            n = g;
            Wd(a, n, j);
            i = o;
            return
        }

        function jd(a, d, f, g, h, j, k, l, m, n, o, p, q, r, s, t, u, v, w, x) {
            a = a | 0;
            d = d | 0;
            f = f | 0;
            g = g | 0;
            h = h | 0;
            j = j | 0;
            k = k | 0;
            l = l | 0;
            m = m | 0;
            n = n | 0;
            o = o | 0;
            p = p | 0;
            q = q | 0;
            r = r | 0;
            s = s | 0;
            t = t | 0;
            u = u | 0;
            v = v | 0;
            w = w | 0;
            x = x | 0;
            var y = 0, z = 0, A = 0, B = 0, C = 0, D = 0, E = 0, F = 0, G = 0, H = 0, I = 0, J = 0, K = 0, L = 0, M = 0,
                N = 0, O = 0, P = 0, Q = 0, R = 0, S = 0, T = 0, U = 0, V = 0, W = 0, X = 0, Y = 0, _ = 0, $ = 0,
                aa = 0, ba = 0, ca = 0, da = 0, ea = 0, fa = 0, ga = 0, ha = 0;
            ha = i;
            i = i + 80 | 0;
            da = ha + 66 | 0;
            ea = ha + 64 | 0;
            fa = ha + 62 | 0;
            ga = ha + 60 | 0;
            O = ha + 40 | 0;
            P = ha + 20 | 0;
            M = ha;
            b[da >> 1] = d;
            b[ea >> 1] = m;
            b[fa >> 1] = n;
            L = re(14, f, x) | 0;
            ca = L & 65535;
            b[ga >> 1] = ca;
            N = re(14, n, x) | 0;
            K = (e[g >> 1] | 0) + 65523 | 0;
            b[M >> 1] = K;
            E = (e[g + 2 >> 1] | 0) + 65522 | 0;
            F = M + 2 | 0;
            b[F >> 1] = E;
            G = ((d & 65535) << 16) + -720896 | 0;
            B = G >> 16;
            G = (G >>> 15) + 15 + (e[g + 4 >> 1] | 0) | 0;
            H = M + 4 | 0;
            b[H >> 1] = G;
            I = (e[g + 6 >> 1] | 0) + B | 0;
            J = M + 6 | 0;
            b[J >> 1] = I;
            B = B + 1 + (e[g + 8 >> 1] | 0) | 0;
            C = M + 8 | 0;
            b[C >> 1] = B;
            y = (e[o >> 1] | 0) + 65523 & 65535;
            b[M + 10 >> 1] = y;
            D = (e[o + 2 >> 1] | 0) + 65522 & 65535;
            b[M + 12 >> 1] = D;
            z = ((m & 65535) << 16) + -720896 | 0;
            g = z >> 16;
            z = (z >>> 15) + 15 + (e[o + 4 >> 1] | 0) & 65535;
            b[M + 14 >> 1] = z;
            A = (e[o + 6 >> 1] | 0) + g & 65535;
            b[M + 16 >> 1] = A;
            g = g + 1 + (e[o + 8 >> 1] | 0) & 65535;
            b[M + 18 >> 1] = g;
            aa = (j & 65535) - (q & 65535) << 16;
            m = aa >> 16;
            if ((aa | 0) > 0) {
                n = k;
                f = r << 16 >> 16 >> m & 65535
            } else {
                n = k << 16 >> 16 >> 0 - m & 65535;
                f = r
            }
            if ((Ee(f, 1, x) | 0) << 16 >> 16 > n << 16 >> 16) f = 1; else f = (((n << 16 >> 16) + 3 >> 2 | 0) > (f << 16 >> 16 | 0)) << 31 >> 31;
            o = K + f & 65535;
            b[M >> 1] = o;
            aa = E + f & 65535;
            b[F >> 1] = aa;
            $ = G + f & 65535;
            b[H >> 1] = $;
            _ = I + f & 65535;
            b[J >> 1] = _;
            Y = B + f & 65535;
            b[C >> 1] = Y;
            m = g << 16 >> 16 > o << 16 >> 16 ? g : o;
            m = A << 16 >> 16 > m << 16 >> 16 ? A : m;
            m = z << 16 >> 16 > m << 16 >> 16 ? z : m;
            m = D << 16 >> 16 > m << 16 >> 16 ? D : m;
            m = y << 16 >> 16 > m << 16 >> 16 ? y : m;
            m = Y << 16 >> 16 > m << 16 >> 16 ? Y : m;
            m = _ << 16 >> 16 > m << 16 >> 16 ? _ : m;
            m = $ << 16 >> 16 > m << 16 >> 16 ? $ : m;
            m = (aa << 16 >> 16 > m << 16 >> 16 ? aa : m) + 1 & 65535;
            g = 0;
            while (1) {
                f = m - (o & 65535) | 0;
                o = f & 65535;
                n = e[h >> 1] << 16;
                f = f << 16 >> 16;
                if (o << 16 >> 16 > 0) o = o << 16 >> 16 < 31 ? n >> f : 0; else {
                    _abort();//fix cc 精简
                }
                aa = o >> 16;
                b[O + (g << 1) >> 1] = aa;
                b[P + (g << 1) >> 1] = (o >>> 1) - (aa << 15);
                g = g + 1 | 0;
                if ((g | 0) == 5) {
                    f = 5;
                    n = p;
                    break
                }
                o = b[M + (g << 1) >> 1] | 0;
                h = h + 2 | 0
            }
            while (1) {
                g = m - (y & 65535) | 0;
                y = g & 65535;
                o = e[n >> 1] << 16;
                g = g << 16 >> 16;
                if (y << 16 >> 16 > 0) o = y << 16 >> 16 < 31 ? o >> g : 0; else {
                    _abort();//fix cc 精简
                }
                aa = o >> 16;
                b[O + (f << 1) >> 1] = aa;
                b[P + (f << 1) >> 1] = (o >>> 1) - (aa << 15);
                o = f + 1 | 0;
                if ((o & 65535) << 16 >> 16 == 10) break;
                y = b[M + (o << 1) >> 1] | 0;
                f = o;
                n = n + 2 | 0
            }
            Q = L << 16 >> 16;
            R = b[O >> 1] | 0;
            S = b[P >> 1] | 0;
            T = b[O + 2 >> 1] | 0;
            U = b[P + 2 >> 1] | 0;
            V = b[O + 4 >> 1] | 0;
            W = b[P + 4 >> 1] | 0;
            X = b[O + 6 >> 1] | 0;
            Y = b[P + 6 >> 1] | 0;
            _ = b[O + 8 >> 1] | 0;
            $ = b[P + 8 >> 1] | 0;
            aa = s & 65535;
            q = N << 16 >> 16;
            j = b[O + 10 >> 1] | 0;
            A = b[P + 10 >> 1] | 0;
            z = b[O + 12 >> 1] | 0;
            h = b[P + 12 >> 1] | 0;
            f = b[O + 14 >> 1] | 0;
            n = b[P + 14 >> 1] | 0;
            g = b[O + 16 >> 1] | 0;
            y = b[P + 16 >> 1] | 0;
            B = b[O + 18 >> 1] | 0;
            P = b[P + 18 >> 1] | 0;
            m = 2147483647;
            O = 0;
            o = 0;
            C = 782;
            do {
                M = b[C >> 1] | 0;
                I = (Z(Q, b[C + 2 >> 1] | 0) | 0) >>> 15 << 16;
                p = I >> 16;
                G = M << 1;
                K = (Z(G, M) | 0) >> 16;
                r = Z(K, R) | 0;
                if ((r | 0) == 1073741824) {
                    c[x >> 2] = 1;
                    J = 2147483647
                } else J = r << 1;
                N = (Z(S, K) | 0) >> 15;
                r = J + (N << 1) | 0;
                if ((J ^ N | 0) > 0 & (r ^ J | 0) < 0) {
                    c[x >> 2] = 1;
                    r = (J >>> 31) + 2147483647 | 0
                }
                K = Z(T, M) | 0;
                if ((K | 0) == 1073741824) {
                    c[x >> 2] = 1;
                    J = 2147483647
                } else J = K << 1;
                N = (Z(U, M) | 0) >> 15;
                K = J + (N << 1) | 0;
                if ((J ^ N | 0) > 0 & (K ^ J | 0) < 0) {
                    c[x >> 2] = 1;
                    K = (J >>> 31) + 2147483647 | 0
                }
                I = (Z(I >> 15, p) | 0) >> 16;
                J = Z(V, I) | 0;
                if ((J | 0) == 1073741824) {
                    c[x >> 2] = 1;
                    H = 2147483647
                } else H = J << 1;
                N = (Z(W, I) | 0) >> 15;
                J = H + (N << 1) | 0;
                if ((H ^ N | 0) > 0 & (J ^ H | 0) < 0) {
                    c[x >> 2] = 1;
                    J = (H >>> 31) + 2147483647 | 0
                }
                I = Z(X, p) | 0;
                if ((I | 0) == 1073741824) {
                    c[x >> 2] = 1;
                    H = 2147483647
                } else H = I << 1;
                N = (Z(Y, p) | 0) >> 15;
                I = H + (N << 1) | 0;
                if ((H ^ N | 0) > 0 & (I ^ H | 0) < 0) {
                    c[x >> 2] = 1;
                    N = (H >>> 31) + 2147483647 | 0
                } else N = I;
                H = (Z(G, p) | 0) >> 16;
                I = Z(_, H) | 0;
                if ((I | 0) == 1073741824) {
                    c[x >> 2] = 1;
                    G = 2147483647
                } else G = I << 1;
                L = (Z($, H) | 0) >> 15;
                I = G + (L << 1) | 0;
                if ((G ^ L | 0) > 0 & (I ^ G | 0) < 0) {
                    c[x >> 2] = 1;
                    I = (G >>> 31) + 2147483647 | 0
                }
                H = b[C + 4 >> 1] | 0;
                G = b[C + 6 >> 1] | 0;
                C = C + 8 | 0;
                if ((M - aa & 65535) << 16 >> 16 < 1 ? (ba = H << 16 >> 16, H << 16 >> 16 <= s << 16 >> 16) : 0) {
                    E = (Z(G << 16 >> 16, q) | 0) >>> 15 << 16;
                    M = E >> 16;
                    D = ba << 1;
                    G = (Z(D, ba) | 0) >> 16;
                    H = Z(j, G) | 0;
                    if ((H | 0) == 1073741824) {
                        c[x >> 2] = 1;
                        F = 2147483647
                    } else F = H << 1;
                    L = (Z(A, G) | 0) >> 15;
                    H = F + (L << 1) | 0;
                    if ((F ^ L | 0) > 0 & (H ^ F | 0) < 0) {
                        c[x >> 2] = 1;
                        H = (F >>> 31) + 2147483647 | 0
                    }
                    G = Z(z, ba) | 0;
                    if ((G | 0) == 1073741824) {
                        c[x >> 2] = 1;
                        F = 2147483647
                    } else F = G << 1;
                    L = (Z(h, ba) | 0) >> 15;
                    G = F + (L << 1) | 0;
                    if ((F ^ L | 0) > 0 & (G ^ F | 0) < 0) {
                        c[x >> 2] = 1;
                        L = (F >>> 31) + 2147483647 | 0
                    } else L = G;
                    F = (Z(E >> 15, M) | 0) >> 16;
                    G = Z(f, F) | 0;
                    if ((G | 0) == 1073741824) {
                        c[x >> 2] = 1;
                        E = 2147483647
                    } else E = G << 1;
                    p = (Z(n, F) | 0) >> 15;
                    G = E + (p << 1) | 0;
                    if ((E ^ p | 0) > 0 & (G ^ E | 0) < 0) {
                        c[x >> 2] = 1;
                        p = (E >>> 31) + 2147483647 | 0
                    } else p = G;
                    G = Z(g, M) | 0;
                    if ((G | 0) == 1073741824) {
                        c[x >> 2] = 1;
                        F = 2147483647
                    } else F = G << 1;
                    E = (Z(y, M) | 0) >> 15;
                    G = F + (E << 1) | 0;
                    if ((F ^ E | 0) > 0 & (G ^ F | 0) < 0) {
                        c[x >> 2] = 1;
                        k = (F >>> 31) + 2147483647 | 0
                    } else k = G;
                    F = (Z(D, M) | 0) >> 16;
                    G = Z(B, F) | 0;
                    if ((G | 0) == 1073741824) {
                        c[x >> 2] = 1;
                        E = 2147483647
                    } else E = G << 1;
                    M = (Z(P, F) | 0) >> 15;
                    G = E + (M << 1) | 0;
                    if ((E ^ M | 0) > 0 & (G ^ E | 0) < 0) {
                        c[x >> 2] = 1;
                        G = (E >>> 31) + 2147483647 | 0
                    }
                    M = K + r + J + N + I + H + L + p + k + G | 0;
                    N = (M | 0) < (m | 0);
                    m = N ? M : m;
                    o = N ? O : o
                }
                O = O + 1 << 16 >> 16
            } while (O << 16 >> 16 < 256);
            s = (o & 65535) << 18 >> 16;
            kd(a, 782 + (s << 1) | 0, ca, d, t, u, x);
            Vd(a, 0, l, ea, fa, da, ga, x);
            l = (re(14, b[fa >> 1] | 0, x) | 0) & 65535;
            kd(a, 782 + ((s | 2) << 1) | 0, l, b[ea >> 1] | 0, v, w, x);
            i = ha;
            return o | 0
        }

        function kd(a, d, f, g, h, j, k) {
            a = a | 0;
            d = d | 0;
            f = f | 0;
            g = g | 0;
            h = h | 0;
            j = j | 0;
            k = k | 0;
            var l = 0, m = 0, n = 0, o = 0;
            o = i;
            i = i + 16 | 0;
            m = o + 2 | 0;
            n = o;
            b[h >> 1] = b[d >> 1] | 0;
            l = b[d + 2 >> 1] | 0;
            f = Z(f << 16 >> 16 << 1, l) | 0;
            h = 10 - (g & 65535) | 0;
            d = h & 65535;
            h = h << 16 >> 16;
            if (d << 16 >> 16 > 0) d = d << 16 >> 16 < 31 ? f >> h : 0; else {
                h = 0 - h << 16 >> 16; //不可精简
                d = f << h;
                d = (d >> h | 0) == (f | 0) ? d : f >> 31 ^ 2147483647
            }
            b[j >> 1] = d >>> 16;
            de(l, m, n, k);
            b[m >> 1] = (e[m >> 1] | 0) + 65524;
            h = Ee(b[n >> 1] | 0, 5, k) | 0;
            g = b[m >> 1] | 0;
            h = ((g & 65535) << 10) + (h & 65535) & 65535;
            f = b[n >> 1] | 0;
            g = g << 16 >> 16;
            if ((g * 24660 | 0) == 1073741824) {
                c[k >> 2] = 1;
                d = 2147483647
            } else d = g * 49320 | 0;
            n = (f << 16 >> 16) * 24660 >> 15;
            g = d + (n << 1) | 0;
            if (!((d ^ n | 0) > 0 & (g ^ d | 0) < 0)) {
                k = g;
                k = k << 13;
                k = k + 32768 | 0;
                k = k >>> 16;
                k = k & 65535;
                Wd(a, h, k);
                i = o;
                return
            }
            c[k >> 2] = 1;
            k = (d >>> 31) + 2147483647 | 0;
            k = k << 13;
            k = k + 32768 | 0;
            k = k >>> 16;
            k = k & 65535;
            Wd(a, h, k);
            i = o;
            return
        }

        function ld(a, d, f, g, h, j, k, l, m, n, o, p, q, r, s, t, u, v, w, x, y) {
            a = a | 0;
            d = d | 0;
            f = f | 0;
            g = g | 0;
            h = h | 0;
            j = j | 0;
            k = k | 0;
            l = l | 0;
            m = m | 0;
            n = n | 0;
            o = o | 0;
            p = p | 0;
            q = q | 0;
            r = r | 0;
            s = s | 0;
            t = t | 0;
            u = u | 0;
            v = v | 0;
            w = w | 0;
            x = x | 0;
            y = y | 0;
            var z = 0, A = 0, B = 0, C = 0, D = 0, E = 0, F = 0, G = 0, H = 0, I = 0, J = 0, K = 0, L = 0, M = 0, N = 0,
                O = 0, P = 0, Q = 0, R = 0, S = 0, T = 0, U = 0, V = 0, W = 0, X = 0, Y = 0, _ = 0, $ = 0, aa = 0,
                ba = 0, ca = 0, da = 0, ea = 0, fa = 0, ga = 0, ha = 0, ia = 0, ja = 0, ka = 0, la = 0;
            la = i;
            i = i + 80 | 0;
            ia = la + 72 | 0;
            ja = la + 70 | 0;
            ka = la + 68 | 0;
            ga = la + 66 | 0;
            ha = la + 56 | 0;
            _ = la + 24 | 0;
            Y = la + 12 | 0;
            W = la + 48 | 0;
            X = la + 40 | 0;
            R = la + 34 | 0;
            T = la + 22 | 0;
            P = la + 6 | 0;
            Q = la;
            nd(5, r, s, P, Q, c[x + 72 >> 2] | 0, y) | 0;
            B = re(14, n, y) | 0;
            S = x + 68 | 0;
            O = c[S >> 2] | 0;
            V = m << 16 >> 16;
            U = V + 65526 | 0;
            r = (e[j >> 1] | 0) + 65523 & 65535;
            b[ha >> 1] = r;
            x = (e[j + 2 >> 1] | 0) + 65522 & 65535;
            b[ha + 2 >> 1] = x;
            da = U << 16 >> 16;
            ea = ((U << 17 >> 17 | 0) == (da | 0) ? U << 1 : da >>> 15 ^ 32767) + 15 + (e[j + 4 >> 1] | 0) & 65535;
            b[ha + 4 >> 1] = ea;
            fa = (e[j + 6 >> 1] | 0) + da & 65535;
            b[ha + 6 >> 1] = fa;
            j = da + 1 + (e[j + 8 >> 1] | 0) & 65535;
            b[ha + 8 >> 1] = j;
            x = x << 16 >> 16 > r << 16 >> 16 ? x : r;
            x = ea << 16 >> 16 > x << 16 >> 16 ? ea : x;
            x = fa << 16 >> 16 > x << 16 >> 16 ? fa : x;
            x = (Rd(j << 16 >> 16 > x << 16 >> 16 ? j : x, 1, y) | 0) & 65535;
            j = r;
            r = 0;
            while (1) {
                n = x - (j & 65535) | 0;
                j = n & 65535;
                A = e[h + (r << 1) >> 1] << 16;
                n = n << 16 >> 16;
                if (j << 16 >> 16 > 0) n = j << 16 >> 16 < 31 ? A >> n : 0; else {
                    _abort();//fix cc 精简
                }
                Nc(n, _ + (r << 1) | 0, Y + (r << 1) | 0, y);
                n = r + 1 | 0;
                if ((n | 0) == 5) break;
                j = b[ha + (n << 1) >> 1] | 0;
                r = n
            }
            M = _ + 2 | 0;
            N = Y + 2 | 0;
            fa = B << 16 >> 16;
            $ = _ + 4 | 0;
            aa = Y + 4 | 0;
            ba = _ + 6 | 0;
            ca = Y + 6 | 0;
            da = _ + 8 | 0;
            ea = Y + 8 | 0;
            E = 0;
            j = 2147483647;
            h = 0;
            n = 0;
            while (1) {
                L = b[P + (h << 1) >> 1] | 0;
                B = Z(L, L) | 0;
                if (B >>> 0 > 1073741823) {
                    c[y >> 2] = 1;
                    B = 32767
                } else B = B >>> 15;
                x = b[Y >> 1] | 0;
                A = B << 16 >> 16;
                B = Z(A, b[_ >> 1] | 0) | 0;
                if ((B | 0) == 1073741824) {
                    c[y >> 2] = 1;
                    r = 2147483647
                } else r = B << 1;
                K = (Z(x << 16 >> 16, A) | 0) >> 15;
                B = r + (K << 1) | 0;
                if ((r ^ K | 0) > 0 & (B ^ r | 0) < 0) {
                    c[y >> 2] = 1;
                    B = (r >>> 31) + 2147483647 | 0
                }
                x = b[N >> 1] | 0;
                A = Z(b[M >> 1] | 0, L) | 0;
                if ((A | 0) != 1073741824) {
                    r = (A << 1) + B | 0;
                    if ((A ^ B | 0) > 0 & (r ^ B | 0) < 0) {
                        c[y >> 2] = 1;
                        r = (B >>> 31) + 2147483647 | 0
                    }
                } else {
                    c[y >> 2] = 1;
                    r = 2147483647
                }
                B = (Z(x << 16 >> 16, L) | 0) >> 15;
                if ((B | 0) > 32767) {
                    c[y >> 2] = 1;
                    B = 32767
                }
                K = B << 16;
                B = (K >> 15) + r | 0;
                if ((K >> 16 ^ r | 0) > 0 & (B ^ r | 0) < 0) {
                    c[y >> 2] = 1;
                    K = (r >>> 31) + 2147483647 | 0
                } else K = B;
                I = (K >>> 31) + 2147483647 | 0;
                J = h & 65535;
                B = E;
                G = 0;
                H = O;
                do {
                    A = (Z(b[H >> 1] | 0, fa) | 0) >> 15;
                    H = H + 6 | 0;
                    if ((A | 0) > 32767) {
                        c[y >> 2] = 1;
                        A = 32767
                    }
                    F = A << 16 >> 16;
                    A = Z(F, F) | 0;
                    if ((A | 0) == 1073741824) {
                        c[y >> 2] = 1;
                        D = 2147483647
                    } else D = A << 1;
                    Nc(D, ia, ja, y);
                    A = Z(F, L) | 0;
                    if ((A | 0) == 1073741824) {
                        c[y >> 2] = 1;
                        D = 2147483647
                    } else D = A << 1;
                    Nc(D, ka, ga, y);
                    r = b[aa >> 1] | 0;
                    C = b[ja >> 1] | 0;
                    A = b[$ >> 1] | 0;
                    x = b[ia >> 1] | 0;
                    E = Z(x, A) | 0;
                    if ((E | 0) != 1073741824) {
                        D = (E << 1) + K | 0;
                        if ((E ^ K | 0) > 0 & (D ^ K | 0) < 0) {
                            c[y >> 2] = 1;
                            D = I
                        }
                    } else {
                        c[y >> 2] = 1;
                        D = 2147483647
                    }
                    E = (Z(C << 16 >> 16, A) | 0) >> 15;
                    if ((E | 0) > 32767) {
                        c[y >> 2] = 1;
                        E = 32767
                    }
                    C = E << 16;
                    E = (C >> 15) + D | 0;
                    if ((C >> 16 ^ D | 0) > 0 & (E ^ D | 0) < 0) {
                        c[y >> 2] = 1;
                        E = (D >>> 31) + 2147483647 | 0
                    }
                    D = (Z(x, r << 16 >> 16) | 0) >> 15;
                    if ((D | 0) > 32767) {
                        c[y >> 2] = 1;
                        D = 32767
                    }
                    C = D << 16;
                    D = (C >> 15) + E | 0;
                    if ((C >> 16 ^ E | 0) > 0 & (D ^ E | 0) < 0) {
                        c[y >> 2] = 1;
                        D = (E >>> 31) + 2147483647 | 0
                    }
                    A = b[ca >> 1] | 0;
                    E = Z(b[ba >> 1] | 0, F) | 0;
                    if ((E | 0) != 1073741824) {
                        C = (E << 1) + D | 0;
                        if ((E ^ D | 0) > 0 & (C ^ D | 0) < 0) {
                            _abort();//fix cc 精简
                        }
                    } else {
                        c[y >> 2] = 1;
                        C = 2147483647
                    }
                    A = (Z(A << 16 >> 16, F) | 0) >> 15;
                    if ((A | 0) > 32767) {
                        c[y >> 2] = 1;
                        A = 32767
                    }
                    F = A << 16;
                    A = (F >> 15) + C | 0;
                    if ((F >> 16 ^ C | 0) > 0 & (A ^ C | 0) < 0) {
                        c[y >> 2] = 1;
                        A = (C >>> 31) + 2147483647 | 0
                    }
                    x = b[ea >> 1] | 0;
                    C = b[ga >> 1] | 0;
                    r = b[da >> 1] | 0;
                    z = b[ka >> 1] | 0;
                    E = Z(z, r) | 0;
                    do if ((E | 0) == 1073741824) {
                        c[y >> 2] = 1;
                        E = 2147483647
                    } else {
                        D = (E << 1) + A | 0;
                        if (!((E ^ A | 0) > 0 & (D ^ A | 0) < 0)) {
                            E = D;
                            break
                        }
                        c[y >> 2] = 1;
                        E = (A >>> 31) + 2147483647 | 0
                    } while (0);
                    D = (Z(C << 16 >> 16, r) | 0) >> 15;
                    if ((D | 0) > 32767) {
                        c[y >> 2] = 1;
                        D = 32767
                    }
                    F = D << 16;
                    D = (F >> 15) + E | 0;
                    if ((F >> 16 ^ E | 0) > 0 & (D ^ E | 0) < 0) {
                        c[y >> 2] = 1;
                        D = (E >>> 31) + 2147483647 | 0
                    }
                    A = (Z(z, x << 16 >> 16) | 0) >> 15;
                    if ((A | 0) > 32767) {
                        c[y >> 2] = 1;
                        A = 32767
                    }
                    F = A << 16;
                    A = (F >> 15) + D | 0;
                    if ((F >> 16 ^ D | 0) > 0 & (A ^ D | 0) < 0) {
                        c[y >> 2] = 1;
                        A = (D >>> 31) + 2147483647 | 0
                    }
                    F = (A | 0) < (j | 0);
                    B = F ? G : B;
                    n = F ? J : n;
                    j = F ? A : j;
                    G = G + 1 << 16 >> 16
                } while (G << 16 >> 16 < 32);
                h = h + 1 | 0;
                if ((h | 0) == 3) {
                    A = B;
                    h = n;
                    break
                } else E = B
            }
            N = (A << 16 >> 16) * 3 | 0;
            j = b[O + (N << 1) >> 1] | 0;
            b[u >> 1] = b[O + (N + 1 << 1) >> 1] | 0;
            b[v >> 1] = b[O + (N + 2 << 1) >> 1] | 0;
            j = Z(j << 16 >> 16, fa) | 0;
            if ((j | 0) == 1073741824) {
                c[y >> 2] = 1;
                B = 2147483647
            } else B = j << 1;
            N = 9 - V | 0;
            O = N & 65535;
            N = N << 16 >> 16;
            M = O << 16 >> 16 > 0;
            if (M) B = O << 16 >> 16 < 31 ? B >> N : 0; else {
                K = 0 - N << 16 >> 16;
                L = B << K;
                B = (L >> K | 0) == (B | 0) ? L : B >> 31 ^ 2147483647
            }
            b[t >> 1] = B >>> 16;
            L = h << 16 >> 16;
            P = b[P + (L << 1) >> 1] | 0;
            b[s >> 1] = P;
            Q = b[Q + (L << 1) >> 1] | 0;
            Ub(d, f, g, P, o, W, X, R, y);
            xc(a, b[R >> 1] | 0, b[t >> 1] | 0, T, y);
            if (!((b[W >> 1] | 0) != 0 & (b[T >> 1] | 0) > 0)) {
                y = A;
                u = c[w >> 2] | 0;
                t = u + 2 | 0;
                b[u >> 1] = Q;
                u = u + 4 | 0;
                c[w >> 2] = u;
                b[t >> 1] = y;
                i = la;
                return
            }
            F = W + 6 | 0;
            b[F >> 1] = l;
            D = X + 6 | 0;
            b[D >> 1] = k;
            m = ((Ge(q, m, y) | 0) & 65535) + 10 | 0;
            x = m << 16 >> 16;
            if ((m & 65535) << 16 >> 16 < 0) {//不可精简
                n = 0 - x << 16;
                if ((n | 0) < 983040) p = p << 16 >> 16 >> (n >> 16) & 65535; else p = 0
            } else {
                n = p << 16 >> 16;
                r = n << x;
                if ((r << 16 >> 16 >> x | 0) == (n | 0)) p = r & 65535; else p = (n >>> 15 ^ 32767) & 65535
            }
            j = b[s >> 1] | 0;
            B = b[T >> 1] | 0;
            S = c[S >> 2] | 0;
            r = b[t >> 1] | 0;
            T = 10 - V | 0;
            x = T << 16 >> 16;
            if ((T & 65535) << 16 >> 16 < 0) {//不可精简
                n = 0 - x << 16;
                if ((n | 0) < 983040) l = r << 16 >> 16 >> (n >> 16) & 65535; else l = 0
            } else {
                n = r << 16 >> 16;
                r = n << x;
                if ((r << 16 >> 16 >> x | 0) == (n | 0)) l = r & 65535; else l = (n >>> 15 ^ 32767) & 65535
            }
            h = j << 16 >> 16;
            n = Z(h, h) | 0;
            if (n >>> 0 > 1073741823) {
                c[y >> 2] = 1;
                j = 32767
            } else j = n >>> 15;
            A = Rd(32767 - (B & 65535) & 65535, 1, y) | 0;
            B = B << 16 >> 16;
            n = Z(b[W + 2 >> 1] | 0, B) | 0;
            if ((n | 0) == 1073741824) {
                c[y >> 2] = 1;
                n = 2147483647
            } else n = n << 1;
            T = n << 1;
            n = Z(((T >> 1 | 0) == (n | 0) ? T : n >> 31 ^ 2147418112) >> 16, j << 16 >> 16) | 0;
            if ((n | 0) == 1073741824) {
                c[y >> 2] = 1;
                E = 2147483647
            } else E = n << 1;
            C = (e[X + 2 >> 1] | 0) + 65521 | 0;
            x = C & 65535;
            n = Z(b[W + 4 >> 1] | 0, B) | 0;
            if ((n | 0) == 1073741824) {
                c[y >> 2] = 1;
                j = 2147483647
            } else j = n << 1;
            n = j << 1;
            n = (Z(((n >> 1 | 0) == (j | 0) ? n : j >> 31 ^ 2147418112) >> 16, h) | 0) >> 15;
            if ((n | 0) > 32767) {
                c[y >> 2] = 1;
                n = 32767
            }
            b[$ >> 1] = n;
            j = U & 65535;
            b[ia >> 1] = j;
            j = Rd(b[X + 4 >> 1] | 0, j, y) | 0;
            n = Z(b[F >> 1] | 0, B) | 0;
            if ((n | 0) == 1073741824) {
                c[y >> 2] = 1;
                n = 2147483647
            } else n = n << 1;
            z = n << 1;
            b[ba >> 1] = ((z >> 1 | 0) == (n | 0) ? z : n >> 31 ^ 2147418112) >>> 16;
            z = ((V << 17 >> 17 | 0) == (V | 0) ? V << 1 : V >>> 15 ^ 32767) + 65529 & 65535;
            b[ia >> 1] = z;
            z = Rd(b[D >> 1] | 0, z, y) | 0;
            n = (Z(b[F >> 1] | 0, A << 16 >> 16) | 0) >> 15;
            if ((n | 0) > 32767) {
                c[y >> 2] = 1;
                n = 32767
            }
            b[da >> 1] = n;
            A = Rd(z, 1, y) | 0;
            r = Z(b[W >> 1] | 0, B) | 0;
            if ((r | 0) == 1073741824) {
                c[y >> 2] = 1;
                n = 2147483647
            } else n = r << 1;
            D = Fe(n, ia, y) | 0;
            h = (e[ia >> 1] | 0) + 47 | 0;
            b[ia >> 1] = h;
            h = (e[X >> 1] | 0) - (h & 65535) | 0;
            B = h + 31 & 65535;
            B = x << 16 >> 16 > B << 16 >> 16 ? x : B;
            B = j << 16 >> 16 > B << 16 >> 16 ? j : B;
            B = z << 16 >> 16 > B << 16 >> 16 ? z : B;
            B = (A << 16 >> 16 > B << 16 >> 16 ? A : B) << 16 >> 16;
            r = B - (C & 65535) | 0;
            n = r & 65535;
            r = r << 16 >> 16;
            if (n << 16 >> 16 > 0) K = n << 16 >> 16 < 31 ? E >> r : 0; else {
                X = 0 - r << 16 >> 16;
                K = E << X;
                K = (K >> X | 0) == (E | 0) ? K : E >> 31 ^ 2147483647
            }
            x = B - (j & 65535) | 0;
            n = x & 65535;
            r = e[$ >> 1] << 16;
            x = x << 16 >> 16;
            if (n << 16 >> 16 > 0) r = n << 16 >> 16 < 31 ? r >> x : 0; else {
                W = 0 - x << 16 >> 16; //不可精简
                X = r << W;
                r = (X >> W | 0) == (r | 0) ? X : r >> 31 ^ 2147483647
            }
            Nc(r, $, aa, y);
            z = B - (z & 65535) | 0;
            r = z & 65535;
            x = e[ba >> 1] << 16;
            z = z << 16 >> 16;
            if (r << 16 >> 16 > 0) r = r << 16 >> 16 < 31 ? x >> z : 0; else {
                _abort();//fix cc 精简
            }
            Nc(r, ba, ca, y);
            z = B - (A & 65535) | 0;
            r = z & 65535;
            x = e[da >> 1] << 16;
            z = z << 16 >> 16;
            if (r << 16 >> 16 > 0) r = r << 16 >> 16 < 31 ? x >> z : 0; else {
                X = 0 - z << 16 >> 16; //不可精简
                r = x << X;
                r = (r >> X | 0) == (x | 0) ? r : x >> 31 ^ 2147483647
            }
            Nc(r, da, ea, y);
            z = B + 65505 | 0;
            b[ia >> 1] = z;
            z = z - (h & 65535) | 0;
            r = De(z & 65535, 1, y) | 0;
            x = r << 16 >> 16;
            if (r << 16 >> 16 > 0) x = r << 16 >> 16 < 31 ? D >> x : 0; else {
                X = 0 - x << 16 >> 16;//不可精简
                x = D << X;
                x = (x >> X | 0) == (D | 0) ? x : D >> 31 ^ 2147483647
            }
            do if (!(z & 1)) E = x; else {//不可精简
                Nc(x, _, Y, y);
                r = b[Y >> 1] | 0;
                x = b[_ >> 1] | 0;
                if ((x * 23170 | 0) == 1073741824) {
                    c[y >> 2] = 1;
                    z = 2147483647
                } else z = x * 46340 | 0;
                _ = (r << 16 >> 16) * 23170 >> 15;
                x = z + (_ << 1) | 0;
                if (!((z ^ _ | 0) > 0 & (x ^ z | 0) < 0)) {
                    E = x;
                    break
                }
                c[y >> 2] = 1;
                E = (z >>> 31) + 2147483647 | 0
            } while (0);
            F = (K >>> 31) + 2147483647 | 0;
            D = 2147483647;
            C = 0;
            x = 0;
            G = S;
            while (1) {
                r = (Z(b[G >> 1] | 0, fa) | 0) >> 15;
                G = G + 6 | 0;
                if ((r | 0) > 32767) {
                    c[y >> 2] = 1;
                    r = 32767
                }
                z = r & 65535;
                if (z << 16 >> 16 >= l << 16 >> 16) break;
                j = r << 16 >> 16;
                r = Z(j, j) | 0;
                if ((r | 0) == 1073741824) {
                    c[y >> 2] = 1;
                    n = 2147483647
                } else n = r << 1;
                Nc(n, ja, ka, y);
                r = (Ge(z, p, y) | 0) << 16 >> 16;
                r = Z(r, r) | 0;
                if ((r | 0) == 1073741824) {
                    c[y >> 2] = 1;
                    r = 2147483647
                } else r = r << 1;
                Nc(r, ga, ha, y);
                z = b[aa >> 1] | 0;
                n = Z(b[$ >> 1] | 0, j) | 0;
                do if ((n | 0) == 1073741824) {
                    c[y >> 2] = 1;
                    n = 2147483647
                } else {
                    r = (n << 1) + K | 0;
                    if (!((n ^ K | 0) > 0 & (r ^ K | 0) < 0)) {
                        n = r;
                        break
                    }
                    c[y >> 2] = 1;
                    n = F
                } while (0);
                r = (Z(z << 16 >> 16, j) | 0) >> 15;
                if ((r | 0) > 32767) {
                    c[y >> 2] = 1;
                    r = 32767
                }
                _ = r << 16;
                r = (_ >> 15) + n | 0;
                if ((_ >> 16 ^ n | 0) > 0 & (r ^ n | 0) < 0) {
                    c[y >> 2] = 1;
                    r = (n >>> 31) + 2147483647 | 0
                }
                h = b[ca >> 1] | 0;
                A = b[ka >> 1] | 0;
                j = b[ba >> 1] | 0;
                B = b[ja >> 1] | 0;
                n = Z(B, j) | 0;
                do if ((n | 0) == 1073741824) {
                    c[y >> 2] = 1;
                    z = 2147483647
                } else {
                    z = (n << 1) + r | 0;
                    if (!((n ^ r | 0) > 0 & (z ^ r | 0) < 0)) break;
                    c[y >> 2] = 1;
                    z = (r >>> 31) + 2147483647 | 0
                } while (0);
                n = (Z(A << 16 >> 16, j) | 0) >> 15;
                if ((n | 0) > 32767) {
                    c[y >> 2] = 1;
                    n = 32767
                }
                _ = n << 16;
                n = (_ >> 15) + z | 0;
                if ((_ >> 16 ^ z | 0) > 0 & (n ^ z | 0) < 0) {
                    c[y >> 2] = 1;
                    n = (z >>> 31) + 2147483647 | 0
                }
                r = (Z(B, h << 16 >> 16) | 0) >> 15;
                if ((r | 0) > 32767) {
                    c[y >> 2] = 1;
                    r = 32767
                }
                _ = r << 16;
                r = (_ >> 15) + n | 0;
                if ((_ >> 16 ^ n | 0) > 0 & (r ^ n | 0) < 0) {
                    c[y >> 2] = 1;
                    r = (n >>> 31) + 2147483647 | 0
                }
                r = Fe(r, ia, y) | 0;
                z = De(b[ia >> 1] | 0, 1, y) | 0;
                n = z << 16 >> 16;
                if (z << 16 >> 16 > 0) z = z << 16 >> 16 < 31 ? r >> n : 0; else {
                    _ = 0 - n << 16 >> 16;
                    z = r << _;
                    z = (z >> _ | 0) == (r | 0) ? z : r >> 31 ^ 2147483647
                }
                r = z - E | 0;
                if (((r ^ z) & (z ^ E) | 0) < 0) {
                    c[y >> 2] = 1;
                    r = (z >>> 31) + 2147483647 | 0
                }
                r = (Ce(r, y) | 0) << 16 >> 16;
                r = Z(r, r) | 0;
                if ((r | 0) == 1073741824) {
                    c[y >> 2] = 1;
                    z = 2147483647
                } else z = r << 1;
                B = b[ea >> 1] | 0;
                j = b[ha >> 1] | 0;
                A = b[da >> 1] | 0;
                h = b[ga >> 1] | 0;
                n = Z(h, A) | 0;
                do if ((n | 0) == 1073741824) {
                    c[y >> 2] = 1;
                    r = 2147483647
                } else {
                    r = (n << 1) + z | 0;
                    if (!((n ^ z | 0) > 0 & (r ^ z | 0) < 0)) break;
                    c[y >> 2] = 1;
                    r = (z >>> 31) + 2147483647 | 0
                } while (0);
                n = (Z(j << 16 >> 16, A) | 0) >> 15;
                if ((n | 0) > 32767) {
                    c[y >> 2] = 1;
                    n = 32767
                }
                _ = n << 16;
                n = (_ >> 15) + r | 0;
                if ((_ >> 16 ^ r | 0) > 0 & (n ^ r | 0) < 0) {
                    c[y >> 2] = 1;
                    n = (r >>> 31) + 2147483647 | 0
                }
                r = (Z(h, B << 16 >> 16) | 0) >> 15;
                if ((r | 0) > 32767) {
                    c[y >> 2] = 1;
                    r = 32767
                }
                _ = r << 16;
                r = (_ >> 15) + n | 0;
                if ((_ >> 16 ^ n | 0) > 0 & (r ^ n | 0) < 0) {
                    c[y >> 2] = 1;
                    r = (n >>> 31) + 2147483647 | 0
                }
                n = (r | 0) < (D | 0);
                x = n ? C : x;
                C = C + 1 << 16 >> 16;
                if (C << 16 >> 16 >= 32) break; else D = n ? r : D
            }
            ka = (x << 16 >> 16) * 3 | 0;
            z = b[S + (ka << 1) >> 1] | 0;
            b[u >> 1] = b[S + (ka + 1 << 1) >> 1] | 0;
            b[v >> 1] = b[S + (ka + 2 << 1) >> 1] | 0;
            z = Z(z << 16 >> 16, fa) | 0;
            if ((z | 0) == 1073741824) {
                c[y >> 2] = 1;
                z = 2147483647
            } else z = z << 1;
            if (M) z = O << 16 >> 16 < 31 ? z >> N : 0; else {//不可精简
                u = 0 - N << 16 >> 16;
                y = z << u;
                z = (y >> u | 0) == (z | 0) ? y : z >> 31 ^ 2147483647
            }
            b[t >> 1] = z >>> 16;
            y = x;
            u = c[w >> 2] | 0;
            t = u + 2 | 0;
            b[u >> 1] = Q;
            u = u + 4 | 0;
            c[w >> 2] = u;
            b[t >> 1] = y;
            i = la;
            return
        }

        function md(a, c, d, e, f, g, h, i) {
            a = a | 0;
            c = c | 0;
            d = d | 0;
            e = e | 0;
            f = f | 0;
            g = g | 0;
            h = h | 0;
            i = i | 0;
            var j = 0, k = 0, l = 0, m = 0, n = 0;
            n = (a | 0) == 7;
            j = b[e >> 1] | 0;
            if (n) {
                j = j << 16 >> 16 >>> 1 & 65535;
                m = re(c, d, i) | 0;
                c = m << 16;
                a = c >> 16;
                if ((m << 20 >> 20 | 0) == (a | 0)) a = c >> 12; else a = a >>> 15 ^ 32767
            } else {
                _abort();//fix cc 精简
            }
            m = a << 16 >> 16;
            i = j << 16 >> 16;
            c = i - ((Z(m, b[h >> 1] | 0) | 0) >>> 15 & 65535) | 0;
            c = ((c & 32768 | 0) != 0 ? 0 - c | 0 : c) & 65535;
            k = 1;
            a = 0;
            l = h;
            while (1) {
                l = l + 6 | 0;
                j = i - ((Z(b[l >> 1] | 0, m) | 0) >>> 15 & 65535) | 0;
                d = j << 16;
                j = (d | 0) < 0 ? 0 - (d >> 16) | 0 : j;
                d = (j << 16 >> 16 | 0) < (c << 16 >> 16 | 0);
                a = d ? k : a;
                k = k + 1 << 16 >> 16;
                if (k << 16 >> 16 >= 32) break; else c = d ? j & 65535 : c
            }
            l = (a << 16 >> 16) * 196608 >> 16;
            b[e >> 1] = (Z(b[h + (l << 1) >> 1] | 0, m) | 0) >>> 15 << (n & 1);
            b[f >> 1] = b[h + (l + 1 << 1) >> 1] | 0;
            b[g >> 1] = b[h + (l + 2 << 1) >> 1] | 0;
            return a | 0
        }

        function nd(a, c, d, e, f, g, h) {
            a = a | 0;
            c = c | 0;
            d = d | 0;
            e = e | 0;
            f = f | 0;
            g = g | 0;
            h = h | 0;
            var i = 0, j = 0, k = 0, l = 0, m = 0, n = 0;
            i = Ge(b[d >> 1] | 0, b[g >> 1] | 0, h) | 0;
            i = (i & 65535) - ((i & 65535) >>> 15 & 65535) | 0;
            i = (i << 16 >> 31 ^ i) & 65535;
            k = 0;
            l = 1;
            while (1) {
                j = b[g + (l << 1) >> 1] | 0;
                if (j << 16 >> 16 > c << 16 >> 16) j = i; else {
                    j = Ge(b[d >> 1] | 0, j, h) | 0;
                    j = (j & 65535) - ((j & 65535) >>> 15 & 65535) | 0;
                    j = (j << 16 >> 31 ^ j) & 65535;
                    n = j << 16 >> 16 < i << 16 >> 16;
                    j = n ? j : i;
                    k = n ? l & 65535 : k
                }
                l = l + 1 | 0;
                if ((l | 0) == 16) break; else i = j
            }
            if ((a | 0) != 5) {
                i = b[g + (k << 16 >> 16 << 1) >> 1] | 0;
                if ((a | 0) == 7) {
                    b[d >> 1] = i & 65532;
                    return k | 0
                } else {
                    b[d >> 1] = i;
                    return k | 0
                }
            }
            j = k << 16 >> 16;
            switch (k << 16 >> 16) {
                case 0: {
                    i = 0;
                    break
                }
                case 15: {
                    m = 8;
                    break
                }
                default:
                    if ((b[g + (j + 1 << 1) >> 1] | 0) > c << 16 >> 16) m = 8; else i = j + 65535 & 65535
            }

            if ((m | 0) == 8) i = j + 65534 & 65535;
            b[f >> 1] = i;
            n = i << 16 >> 16;
            b[e >> 1] = b[g + (n << 1) >> 1] | 0;
            n = n + 1 | 0;
            b[f + 2 >> 1] = n;
            n = n << 16 >> 16;
            b[e + 2 >> 1] = b[g + (n << 1) >> 1] | 0;
            n = n + 1 | 0;
            b[f + 4 >> 1] = n;
            b[e + 4 >> 1] = b[g + (n << 16 >> 16 << 1) >> 1] | 0;
            b[d >> 1] = b[g + (j << 1) >> 1] | 0;
            return k | 0
        }

        function od(a, d, f, g, h, j, k, l, m, n, o, p) {
            a = a | 0;
            d = d | 0;
            f = f | 0;
            g = g | 0;
            h = h | 0;
            j = j | 0;
            k = k | 0;
            l = l | 0;
            m = m | 0;
            n = n | 0;
            o = o | 0;
            p = p | 0;
            var q = 0, r = 0, s = 0, t = 0, u = 0, v = 0, w = 0, x = 0, y = 0, z = 0, A = 0, B = 0, C = 0, D = 0, E = 0,
                F = 0, G = 0, H = 0, I = 0, J = 0, K = 0;
            K = i;
            i = i + 32 | 0;
            s = K + 20 | 0;
            t = K + 10 | 0;
            r = K;
            switch (a | 0) {
                case 3:
                case 4:
                case 6: {
                    o = o + 84 | 0;
                    J = 128;
                    break
                }
                default: {
                    o = o + 80 | 0;
                    J = 64
                }
            }
            I = c[o >> 2] | 0;
            q = re(14, f, p) | 0;
            H = d << 16 >> 16;
            G = H + 65525 | 0;
            a = (e[h >> 1] | 0) + 65523 & 65535;
            b[r >> 1] = a;
            d = (e[h + 2 >> 1] | 0) + 65522 & 65535;
            b[r + 2 >> 1] = d;
            F = G << 16 >> 16;
            F = Rd(b[h + 4 >> 1] | 0, ((G << 17 >> 17 | 0) == (F | 0) ? G << 1 : F >>> 15 ^ 32767) + 15 & 65535, p) | 0;
            b[r + 4 >> 1] = F;
            G = Rd(b[h + 6 >> 1] | 0, G & 65535, p) | 0;
            b[r + 6 >> 1] = G;
            h = Rd(b[h + 8 >> 1] | 0, H + 65526 & 65535, p) | 0;
            b[r + 8 >> 1] = h;
            d = d << 16 >> 16 > a << 16 >> 16 ? d : a;
            d = F << 16 >> 16 > d << 16 >> 16 ? F : d;
            d = G << 16 >> 16 > d << 16 >> 16 ? G : d;
            d = (h << 16 >> 16 > d << 16 >> 16 ? h : d) + 1 & 65535;
            h = 0;
            while (1) {
                f = d - (a & 65535) | 0;
                o = f & 65535;
                a = e[g + (h << 1) >> 1] << 16;
                f = f << 16 >> 16;
                if (o << 16 >> 16 > 0) o = o << 16 >> 16 < 31 ? a >> f : 0; else {
                    _abort();//fix cc 精简
                }
                Nc(o, s + (h << 1) | 0, t + (h << 1) | 0, p);
                o = h + 1 | 0;
                if ((o | 0) == 5) break;
                a = b[r + (o << 1) >> 1] | 0;
                h = o
            }
            G = q << 16 >> 16;
            y = b[s >> 1] | 0;
            z = b[t >> 1] | 0;
            A = b[s + 2 >> 1] | 0;
            B = b[t + 2 >> 1] | 0;
            C = b[s + 4 >> 1] | 0;
            D = b[t + 4 >> 1] | 0;
            E = b[s + 6 >> 1] | 0;
            F = b[t + 6 >> 1] | 0;
            x = b[s + 8 >> 1] | 0;
            u = b[t + 8 >> 1] | 0;
            d = 2147483647;
            v = 0;
            o = 0;
            w = I;
            while (1) {
                h = b[w >> 1] | 0;
                if (h << 16 >> 16 > j << 16 >> 16) q = d; else {
                    q = (Z(b[w + 2 >> 1] | 0, G) | 0) >> 15;
                    if ((q | 0) > 32767) {
                        c[p >> 2] = 1;
                        q = 32767
                    }
                    t = h << 16 >> 16;
                    h = Z(t, t) | 0;
                    if (h >>> 0 > 1073741823) {
                        c[p >> 2] = 1;
                        r = 32767
                    } else r = h >>> 15;
                    f = q << 16 >> 16;
                    q = Z(f, f) | 0;
                    if (q >>> 0 > 1073741823) {
                        c[p >> 2] = 1;
                        s = 32767
                    } else s = q >>> 15;
                    g = (Z(f, t) | 0) >> 15;
                    if ((g | 0) > 32767) {
                        c[p >> 2] = 1;
                        g = 32767
                    }
                    q = r << 16 >> 16;
                    r = Z(y, q) | 0;
                    if ((r | 0) == 1073741824) {
                        c[p >> 2] = 1;
                        h = 2147483647
                    } else h = r << 1;
                    q = (Z(z, q) | 0) >> 15;
                    r = h + (q << 1) | 0;
                    if ((h ^ q | 0) > 0 & (r ^ h | 0) < 0) {
                        c[p >> 2] = 1;
                        r = (h >>> 31) + 2147483647 | 0
                    }
                    q = Z(A, t) | 0;
                    if ((q | 0) == 1073741824) {
                        c[p >> 2] = 1;
                        h = 2147483647
                    } else h = q << 1;
                    t = (Z(B, t) | 0) >> 15;
                    q = h + (t << 1) | 0;
                    if ((h ^ t | 0) > 0 & (q ^ h | 0) < 0) {
                        c[p >> 2] = 1;
                        q = (h >>> 31) + 2147483647 | 0
                    }
                    h = q + r | 0;
                    if ((q ^ r | 0) > -1 & (h ^ r | 0) < 0) {
                        c[p >> 2] = 1;
                        h = (r >>> 31) + 2147483647 | 0
                    }
                    q = s << 16 >> 16;
                    r = Z(C, q) | 0;
                    if ((r | 0) == 1073741824) {
                        c[p >> 2] = 1;
                        a = 2147483647
                    } else a = r << 1;
                    t = (Z(D, q) | 0) >> 15;
                    r = a + (t << 1) | 0;
                    if ((a ^ t | 0) > 0 & (r ^ a | 0) < 0) {
                        c[p >> 2] = 1;
                        r = (a >>> 31) + 2147483647 | 0
                    }
                    q = r + h | 0;
                    if ((r ^ h | 0) > -1 & (q ^ h | 0) < 0) {
                        c[p >> 2] = 1;
                        a = (h >>> 31) + 2147483647 | 0
                    } else a = q;
                    q = Z(E, f) | 0;
                    if ((q | 0) == 1073741824) {
                        c[p >> 2] = 1;
                        r = 2147483647
                    } else r = q << 1;
                    t = (Z(F, f) | 0) >> 15;
                    q = r + (t << 1) | 0;
                    if ((r ^ t | 0) > 0 & (q ^ r | 0) < 0) {
                        c[p >> 2] = 1;
                        q = (r >>> 31) + 2147483647 | 0
                    }
                    h = q + a | 0;
                    if ((q ^ a | 0) > -1 & (h ^ a | 0) < 0) {
                        c[p >> 2] = 1;
                        r = (a >>> 31) + 2147483647 | 0
                    } else r = h;
                    h = g << 16 >> 16;
                    q = Z(x, h) | 0;
                    if ((q | 0) == 1073741824) {
                        c[p >> 2] = 1;
                        a = 2147483647
                    } else a = q << 1;
                    t = (Z(u, h) | 0) >> 15;
                    q = a + (t << 1) | 0;
                    if ((a ^ t | 0) > 0 & (q ^ a | 0) < 0) {
                        c[p >> 2] = 1;
                        h = (a >>> 31) + 2147483647 | 0
                    } else h = q;
                    q = h + r | 0;
                    if ((h ^ r | 0) > -1 & (q ^ r | 0) < 0) {
                        c[p >> 2] = 1;
                        q = (r >>> 31) + 2147483647 | 0
                    }
                    t = (q | 0) < (d | 0);
                    q = t ? q : d;
                    o = t ? v : o
                }
                w = w + 8 | 0;
                v = v + 1 << 16 >> 16;
                if ((v << 16 >> 16 | 0) >= (J | 0)) break; else d = q
            }
            j = o << 16 >> 16;
            j = ((j << 18 >> 18 | 0) == (j | 0) ? j << 2 : j >>> 15 ^ 32767) << 16 >> 16;
            b[k >> 1] = b[I + (j << 1) >> 1] | 0;
            d = b[I + (j + 1 << 1) >> 1] | 0;
            b[m >> 1] = b[I + (j + 2 << 1) >> 1] | 0;
            b[n >> 1] = b[I + (j + 3 << 1) >> 1] | 0;
            d = Z(d << 16 >> 16, G) | 0;
            if ((d | 0) == 1073741824) {
                c[p >> 2] = 1;
                a = 2147483647
            } else a = d << 1;
            f = 10 - H | 0;
            d = f & 65535;
            f = f << 16 >> 16;
            if (d << 16 >> 16 > 0) {
                p = d << 16 >> 16 < 31 ? a >> f : 0;
                p = p >>> 16;
                p = p & 65535;
                b[l >> 1] = p;
                i = K;
                return o | 0
            } else {//不可精简
                m = 0 - f << 16 >> 16;
                p = a << m;
                p = (p >> m | 0) == (a | 0) ? p : a >> 31 ^ 2147483647;
                p = p >>> 16;
                p = p & 65535;
                b[l >> 1] = p;
                i = K;
                return o | 0
            }
            return 0
        }

        function pd(a, c, d, f, g, h, j, k, l) {
            a = a | 0;
            c = c | 0;
            d = d | 0;
            f = f | 0;
            g = g | 0;
            h = h | 0;
            j = j | 0;
            k = k | 0;
            l = l | 0;
            var m = 0, n = 0, o = 0, p = 0, q = 0, r = 0, s = 0, t = 0, u = 0, v = 0, w = 0, x = 0, y = 0, z = 0, A = 0,
                B = 0, C = 0, D = 0, E = 0, F = 0, G = 0, H = 0, I = 0, J = 0, K = 0, L = 0, M = 0, N = 0, O = 0, P = 0,
                Q = 0, R = 0, S = 0, T = 0, U = 0, V = 0, W = 0, X = 0, Y = 0, _ = 0, $ = 0, aa = 0, ba = 0, ca = 0,
                da = 0, ea = 0, fa = 0, ga = 0, ha = 0, ia = 0, ja = 0, ka = 0, la = 0, ma = 0, na = 0, oa = 0, pa = 0,
                qa = 0, ra = 0, sa = 0, ta = 0, ua = 0, va = 0, wa = 0;
            wa = i;
            i = i + 160 | 0;
            va = wa;
            n = a << 16 >> 16;
            ta = a << 16 >> 16 == 10;
            ua = b[j + (b[h >> 1] << 1) >> 1] | 0;
            if (a << 16 >> 16 > 0) {
                l = 0;
                m = k;
                while (1) {
                    b[m >> 1] = l;
                    l = l + 1 << 16 >> 16;
                    if (l << 16 >> 16 >= a << 16 >> 16) break; else m = m + 2 | 0
                }
            }
            if (d << 16 >> 16 <= 1) {
                i = wa;
                return
            }
            ra = h + 2 | 0;
            sa = ua << 16 >> 16;
            oa = f + (sa << 1) | 0;
            pa = g + (sa * 80 | 0) + (sa << 1) | 0;
            qa = h + 6 | 0;
            X = c & 65535;
            Y = h + 4 | 0;
            _ = h + 10 | 0;
            $ = h + 8 | 0;
            aa = h + 14 | 0;
            ba = h + 12 | 0;
            ca = h + 18 | 0;
            da = h + 16 | 0;
            ea = k + 2 | 0;
            fa = k + 4 | 0;
            ga = k + 6 | 0;
            ha = k + 8 | 0;
            ia = k + 10 | 0;
            ja = k + 12 | 0;
            ka = k + 14 | 0;
            la = k + 16 | 0;
            ma = k + 18 | 0;
            na = a << 16 >> 16 > 2;
            V = h + (n + -1 << 1) | 0;
            T = 1;
            W = 1;
            N = 0;
            O = 0;
            U = -1;
            while (1) {
                S = b[j + (b[ra >> 1] << 1) >> 1] | 0;
                R = S << 16 >> 16;
                c = (e[f + (R << 1) >> 1] | 0) + (e[oa >> 1] | 0) | 0;
                m = (b[g + (sa * 80 | 0) + (R << 1) >> 1] << 13) + 32768 + ((b[g + (R * 80 | 0) + (R << 1) >> 1] | 0) + (b[pa >> 1] | 0) << 12) | 0;
                n = b[qa >> 1] | 0;
                if (n << 16 >> 16 < 40) {
                    n = n << 16 >> 16;
                    o = va;
                    while (1) {
                        P = (b[g + (n * 80 | 0) + (n << 1) >> 1] | 0) >>> 1;
                        M = b[g + (n * 80 | 0) + (sa << 1) >> 1] | 0;
                        Q = b[g + (n * 80 | 0) + (R << 1) >> 1] | 0;
                        b[o >> 1] = c + (e[f + (n << 1) >> 1] | 0);
                        b[o + 2 >> 1] = (M + 2 + P + Q | 0) >>> 2;
                        n = n + X | 0;
                        if ((n & 65535) << 16 >> 16 < 40) {
                            n = n << 16 >> 16;
                            o = o + 4 | 0
                        } else break
                    }
                    B = b[qa >> 1] | 0
                } else B = n;
                c = b[Y >> 1] | 0;
                A = m >> 12;
                n = c << 16 >> 16;
                a:do if (c << 16 >> 16 < 40) {
                    z = B << 16 >> 16;
                    if (B << 16 >> 16 < 40) {
                        o = 1;
                        q = c;
                        s = B;
                        r = 0;
                        p = -1
                    } else while (1) {
                        _abort();//fix cc 精简
                    }
                    while (1) {
                        y = ((b[g + (n * 80 | 0) + (n << 1) >> 1] | 0) + A >> 1) + (b[g + (n * 80 | 0) + (sa << 1) >> 1] | 0) + (b[g + (n * 80 | 0) + (R << 1) >> 1] | 0) | 0;
                        x = e[f + (n << 1) >> 1] | 0;
                        v = z;
                        w = B;
                        u = va;
                        t = r;
                        while (1) {
                            m = (e[u >> 1] | 0) + x | 0;
                            l = m << 16 >> 16;
                            l = (Z(l, l) | 0) >>> 15;
                            r = (y + (b[g + (n * 80 | 0) + (v << 1) >> 1] | 0) >> 2) + (b[u + 2 >> 1] | 0) >> 1;
                            if ((Z(l << 16 >> 16, o << 16 >> 16) | 0) > (Z(r, p << 16 >> 16) | 0)) {
                                o = r & 65535;
                                q = c;
                                s = w;
                                r = m & 65535;
                                p = l & 65535
                            } else r = t;
                            m = v + X | 0;
                            w = m & 65535;
                            if (w << 16 >> 16 >= 40) break; else {
                                v = m << 16 >> 16;
                                u = u + 4 | 0;
                                t = r
                            }
                        }
                        n = n + X | 0;
                        c = n & 65535;
                        if (c << 16 >> 16 < 40) n = n << 16 >> 16; else {
                            Q = q;
                            P = s;
                            n = r;
                            break
                        }
                    }
                } else {
                    o = 1;
                    Q = c;
                    P = B;
                    n = 0
                } while (0);
                q = o << 16 >> 16 << 15;
                o = b[_ >> 1] | 0;
                if (o << 16 >> 16 < 40) {
                    m = Q << 16 >> 16;
                    l = P << 16 >> 16;
                    c = n & 65535;
                    o = o << 16 >> 16;
                    n = va;
                    while (1) {
                        J = b[g + (o * 80 | 0) + (o << 1) >> 1] >> 1;
                        I = b[g + (o * 80 | 0) + (sa << 1) >> 1] | 0;
                        K = b[g + (o * 80 | 0) + (R << 1) >> 1] | 0;
                        L = b[g + (o * 80 | 0) + (m << 1) >> 1] | 0;
                        M = b[g + (o * 80 | 0) + (l << 1) >> 1] | 0;
                        b[n >> 1] = (e[f + (o << 1) >> 1] | 0) + c;
                        b[n + 2 >> 1] = (I + 2 + J + K + L + M | 0) >>> 2;
                        o = o + X | 0;
                        if ((o & 65535) << 16 >> 16 < 40) {
                            o = o << 16 >> 16;
                            n = n + 4 | 0
                        } else break
                    }
                    J = b[_ >> 1] | 0
                } else J = o;
                p = b[$ >> 1] | 0;
                o = p << 16 >> 16;
                b:do if (p << 16 >> 16 < 40) {
                    C = Q << 16 >> 16;
                    D = P << 16 >> 16;
                    E = J << 16 >> 16;
                    B = q + 32768 | 0;
                    if (J << 16 >> 16 < 40) {
                        r = 1;
                        q = p;
                        c = J;
                        s = p;
                        n = 0;
                        p = -1
                    } else while (1) {
                        _abort();//fix cc 精简
                    }
                    while (1) {
                        l = e[f + (o << 1) >> 1] | 0;
                        A = (b[g + (o * 80 | 0) + (R << 1) >> 1] | 0) + (b[g + (o * 80 | 0) + (sa << 1) >> 1] | 0) + (b[g + (o * 80 | 0) + (C << 1) >> 1] | 0) + (b[g + (o * 80 | 0) + (D << 1) >> 1] | 0) | 0;
                        z = B + (b[g + (o * 80 | 0) + (o << 1) >> 1] << 11) | 0;
                        x = E;
                        v = J;
                        y = va;
                        while (1) {
                            t = (e[y >> 1] | 0) + l | 0;
                            m = z + (b[y + 2 >> 1] << 14) + (A + (b[g + (o * 80 | 0) + (x << 1) >> 1] | 0) << 12) | 0;
                            u = t << 16 >> 16;
                            u = (Z(u, u) | 0) >>> 15;
                            if ((Z(u << 16 >> 16, r << 16 >> 16) | 0) > (Z(m >> 16, p << 16 >> 16) | 0)) {
                                r = m >>> 16 & 65535;
                                w = s;
                                c = v;
                                n = t & 65535;
                                p = u & 65535
                            } else w = q;
                            q = x + X | 0;
                            v = q & 65535;
                            if (v << 16 >> 16 >= 40) {
                                q = w;
                                break
                            } else {
                                x = q << 16 >> 16;
                                q = w;
                                y = y + 4 | 0
                            }
                        }
                        o = o + X | 0;
                        s = o & 65535;
                        if (s << 16 >> 16 < 40) o = o << 16 >> 16; else {
                            o = r;
                            M = q;
                            L = c;
                            break
                        }
                    }
                } else {
                    o = 1;
                    M = p;
                    L = J;
                    n = 0
                } while (0);
                r = o << 16 >> 16 << 15;
                o = b[aa >> 1] | 0;
                if (o << 16 >> 16 < 40) {
                    m = Q << 16 >> 16;
                    l = P << 16 >> 16;
                    p = M << 16 >> 16;
                    q = L << 16 >> 16;
                    c = n & 65535;
                    o = o << 16 >> 16;
                    n = va;
                    while (1) {
                        F = b[g + (o * 80 | 0) + (o << 1) >> 1] >> 1;
                        E = b[g + (sa * 80 | 0) + (o << 1) >> 1] | 0;
                        G = b[g + (R * 80 | 0) + (o << 1) >> 1] | 0;
                        H = b[g + (m * 80 | 0) + (o << 1) >> 1] | 0;
                        I = b[g + (l * 80 | 0) + (o << 1) >> 1] | 0;
                        J = b[g + (p * 80 | 0) + (o << 1) >> 1] | 0;
                        K = b[g + (q * 80 | 0) + (o << 1) >> 1] | 0;
                        b[n >> 1] = (e[f + (o << 1) >> 1] | 0) + c;
                        b[n + 2 >> 1] = (E + 4 + F + G + H + I + J + K | 0) >>> 3;
                        o = o + X | 0;
                        if ((o & 65535) << 16 >> 16 < 40) {
                            o = o << 16 >> 16;
                            n = n + 4 | 0
                        } else break
                    }
                    c = b[aa >> 1] | 0
                } else c = o;
                s = b[ba >> 1] | 0;
                if (s << 16 >> 16 < 40) {
                    J = Q << 16 >> 16;
                    F = P << 16 >> 16;
                    E = M << 16 >> 16;
                    D = L << 16 >> 16;
                    C = c << 16 >> 16;
                    B = c << 16 >> 16 < 40;
                    G = r + 32768 | 0;
                    I = s << 16 >> 16;
                    l = 1;
                    w = s;
                    v = c;
                    H = s;
                    q = 0;
                    o = -1;
                    while (1) {
                        if (B) {
                            r = e[f + (I << 1) >> 1] | 0;
                            n = (b[g + (I * 80 | 0) + (R << 1) >> 1] | 0) + (b[g + (I * 80 | 0) + (sa << 1) >> 1] | 0) + (b[g + (I * 80 | 0) + (J << 1) >> 1] | 0) + (b[g + (I * 80 | 0) + (F << 1) >> 1] | 0) + (b[g + (I * 80 | 0) + (E << 1) >> 1] | 0) + (b[g + (I * 80 | 0) + (D << 1) >> 1] | 0) | 0;
                            p = G + (b[g + (I * 80 | 0) + (I << 1) >> 1] << 10) | 0;
                            u = C;
                            s = c;
                            z = v;
                            A = va;
                            while (1) {
                                y = (e[A >> 1] | 0) + r | 0;
                                v = p + (b[A + 2 >> 1] << 14) + (n + (b[g + (I * 80 | 0) + (u << 1) >> 1] | 0) << 11) | 0;
                                x = y << 16 >> 16;
                                x = (Z(x, x) | 0) >>> 15;
                                if ((Z(x << 16 >> 16, l << 16 >> 16) | 0) > (Z(v >> 16, o << 16 >> 16) | 0)) {
                                    l = v >>> 16 & 65535;
                                    w = H;
                                    v = s;
                                    q = y & 65535;
                                    o = x & 65535
                                } else v = z;
                                t = u + X | 0;
                                s = t & 65535;
                                if (s << 16 >> 16 >= 40) break; else {
                                    u = t << 16 >> 16;
                                    z = v;
                                    A = A + 4 | 0
                                }
                            }
                        }
                        s = I + X | 0;
                        H = s & 65535;
                        if (H << 16 >> 16 >= 40) {
                            K = v;
                            break
                        } else I = s << 16 >> 16
                    }
                } else {
                    l = 1;
                    w = s;
                    K = c;
                    q = 0;
                    o = -1
                }
                if (ta) {
                    u = l << 16 >> 16 << 15;
                    o = b[ca >> 1] | 0;
                    if (o << 16 >> 16 < 40) {
                        n = Q << 16 >> 16;
                        c = P << 16 >> 16;
                        m = M << 16 >> 16;
                        l = L << 16 >> 16;
                        r = w << 16 >> 16;
                        s = K << 16 >> 16;
                        p = q & 65535;
                        o = o << 16 >> 16;
                        q = va;
                        while (1) {
                            E = b[g + (o * 80 | 0) + (o << 1) >> 1] >> 1;
                            D = b[g + (sa * 80 | 0) + (o << 1) >> 1] | 0;
                            F = b[g + (R * 80 | 0) + (o << 1) >> 1] | 0;
                            G = b[g + (n * 80 | 0) + (o << 1) >> 1] | 0;
                            H = b[g + (c * 80 | 0) + (o << 1) >> 1] | 0;
                            I = b[g + (m * 80 | 0) + (o << 1) >> 1] | 0;
                            J = b[g + (l * 80 | 0) + (o << 1) >> 1] | 0;
                            N = b[g + (r * 80 | 0) + (o << 1) >> 1] | 0;
                            O = b[g + (s * 80 | 0) + (o << 1) >> 1] | 0;
                            b[q >> 1] = (e[f + (o << 1) >> 1] | 0) + p;
                            b[q + 2 >> 1] = (D + 4 + E + F + G + H + I + J + N + O | 0) >>> 3;
                            o = o + X | 0;
                            if ((o & 65535) << 16 >> 16 < 40) {
                                o = o << 16 >> 16;
                                q = q + 4 | 0
                            } else break
                        }
                        J = b[ca >> 1] | 0
                    } else J = o;
                    r = b[da >> 1] | 0;
                    if (r << 16 >> 16 < 40) {
                        E = Q << 16 >> 16;
                        D = P << 16 >> 16;
                        C = M << 16 >> 16;
                        m = L << 16 >> 16;
                        F = w << 16 >> 16;
                        G = K << 16 >> 16;
                        H = J << 16 >> 16;
                        I = J << 16 >> 16 < 40;
                        B = u + 32768 | 0;
                        n = r << 16 >> 16;
                        l = 1;
                        s = r;
                        q = J;
                        c = r;
                        o = -1;
                        while (1) {
                            if (I) {
                                u = e[f + (n << 1) >> 1] | 0;
                                p = (b[g + (R * 80 | 0) + (n << 1) >> 1] | 0) + (b[g + (sa * 80 | 0) + (n << 1) >> 1] | 0) + (b[g + (E * 80 | 0) + (n << 1) >> 1] | 0) + (b[g + (D * 80 | 0) + (n << 1) >> 1] | 0) + (b[g + (C * 80 | 0) + (n << 1) >> 1] | 0) + (b[g + (m * 80 | 0) + (n << 1) >> 1] | 0) + (b[g + (F * 80 | 0) + (n << 1) >> 1] | 0) + (b[g + (G * 80 | 0) + (n << 1) >> 1] | 0) | 0;
                                r = B + (b[g + (n * 80 | 0) + (n << 1) >> 1] << 9) | 0;
                                A = H;
                                x = J;
                                z = va;
                                while (1) {
                                    y = (e[z >> 1] | 0) + u << 16 >> 16;
                                    y = (Z(y, y) | 0) >>> 15;
                                    v = r + (b[z + 2 >> 1] << 13) + (p + (b[g + (n * 80 | 0) + (A << 1) >> 1] | 0) << 10) | 0;
                                    if ((Z(y << 16 >> 16, l << 16 >> 16) | 0) > (Z(v >> 16, o << 16 >> 16) | 0)) {
                                        l = v >>> 16 & 65535;
                                        s = c;
                                        q = x;
                                        o = y & 65535
                                    }
                                    t = A + X | 0;
                                    x = t & 65535;
                                    if (x << 16 >> 16 >= 40) break; else {
                                        A = t << 16 >> 16;
                                        z = z + 4 | 0
                                    }
                                }
                            }
                            r = n + X | 0;
                            c = r & 65535;
                            if (c << 16 >> 16 >= 40) break; else n = r << 16 >> 16
                        }
                    } else {
                        l = 1;
                        s = r;
                        q = J;
                        o = -1
                    }
                } else {
                    s = N;
                    q = O
                }
                if ((Z(o << 16 >> 16, T << 16 >> 16) | 0) > (Z(l << 16 >> 16, U << 16 >> 16) | 0)) {
                    b[k >> 1] = ua;
                    b[ea >> 1] = S;
                    b[fa >> 1] = Q;
                    b[ga >> 1] = P;
                    b[ha >> 1] = M;
                    b[ia >> 1] = L;
                    b[ja >> 1] = w;
                    b[ka >> 1] = K;
                    if (ta) {
                        b[la >> 1] = s;
                        b[ma >> 1] = q
                    }
                } else {
                    l = T;
                    o = U
                }
                n = b[ra >> 1] | 0;
                if (na) {
                    c = 1;
                    m = 2;
                    while (1) {
                        b[h + (c << 1) >> 1] = b[h + (m << 1) >> 1] | 0;
                        m = m + 1 | 0;
                        if ((m & 65535) << 16 >> 16 == a << 16 >> 16) break; else c = c + 1 | 0
                    }
                }
                b[V >> 1] = n;
                W = W + 1 << 16 >> 16;
                if (W << 16 >> 16 >= d << 16 >> 16) break; else {
                    T = l;
                    N = s;
                    O = q;
                    U = o
                }
            }
            i = wa;
            return
        }

        function qd(a, c, d, e) {
            a = a | 0;
            c = c | 0;
            d = d | 0;
            e = e | 0;
            var f = 0, g = 0, h = 0, i = 0, j = 0, k = 0;
            i = 39;
            while (1) {
                h = a + (i << 1) | 0;
                g = b[h >> 1] | 0;
                f = c + (i << 1) | 0;
                if (g << 16 >> 16 > -1) b[f >> 1] = 32767; else {
                    b[f >> 1] = -32767;
                    if (g << 16 >> 16 == -32768) g = 32767; else g = 0 - (g & 65535) & 65535;
                    b[h >> 1] = g
                }
                b[d + (i << 1) >> 1] = g;
                if ((i | 0) > 0) i = i + -1 | 0; else break
            }
            k = 8 - (e << 16 >> 16) | 0;
            if ((k | 0) > 0) {
                j = 0;
                f = 0
            } else return;
            do {
                e = 0;
                a = 0;
                h = 32767;
                while (1) {
                    c = b[d + (e << 1) >> 1] | 0;
                    i = c << 16 >> 16 > -1 ? c << 16 >> 16 < h << 16 >> 16 : 0;
                    f = i ? a : f;
                    g = e + 5 | 0;
                    a = g & 65535;
                    if (a << 16 >> 16 >= 40) break; else {
                        e = g << 16 >> 16;
                        h = i ? c : h
                    }
                }
                b[d + (f << 16 >> 16 << 1) >> 1] = -1;
                j = j + 1 << 16 >> 16
            } while ((j << 16 >> 16 | 0) < (k | 0));
            j = 0;
            do {
                c = 1;
                a = 1;
                g = 32767;
                while (1) {
                    e = b[d + (c << 1) >> 1] | 0;
                    i = e << 16 >> 16 > -1 ? e << 16 >> 16 < g << 16 >> 16 : 0;
                    f = i ? a : f;
                    h = c + 5 | 0;
                    a = h & 65535;
                    if (a << 16 >> 16 >= 40) break; else {
                        c = h << 16 >> 16;
                        g = i ? e : g
                    }
                }
                b[d + (f << 16 >> 16 << 1) >> 1] = -1;
                j = j + 1 << 16 >> 16
            } while ((j << 16 >> 16 | 0) < (k | 0));
            j = 0;
            do {
                c = 2;
                a = 2;
                g = 32767;
                while (1) {
                    e = b[d + (c << 1) >> 1] | 0;
                    i = e << 16 >> 16 > -1 ? e << 16 >> 16 < g << 16 >> 16 : 0;
                    f = i ? a : f;
                    h = c + 5 | 0;
                    a = h & 65535;
                    if (a << 16 >> 16 >= 40) break; else {
                        c = h << 16 >> 16;
                        g = i ? e : g
                    }
                }
                b[d + (f << 16 >> 16 << 1) >> 1] = -1;
                j = j + 1 << 16 >> 16
            } while ((j << 16 >> 16 | 0) < (k | 0));
            j = 0;
            while (1) {
                c = 3;
                a = 3;
                g = 32767;
                while (1) {
                    e = b[d + (c << 1) >> 1] | 0;
                    i = e << 16 >> 16 > -1 ? e << 16 >> 16 < g << 16 >> 16 : 0;
                    f = i ? a : f;
                    h = c + 5 | 0;
                    a = h & 65535;
                    if (a << 16 >> 16 >= 40) {
                        g = f;
                        break
                    } else {
                        c = h << 16 >> 16;
                        g = i ? e : g
                    }
                }
                b[d + (g << 16 >> 16 << 1) >> 1] = -1;
                j = j + 1 << 16 >> 16;
                if ((j << 16 >> 16 | 0) >= (k | 0)) {
                    f = 0;
                    break
                } else f = g
            }
            do {
                c = 4;
                a = 4;
                j = 32767;
                while (1) {
                    e = b[d + (c << 1) >> 1] | 0;
                    i = e << 16 >> 16 > -1 ? e << 16 >> 16 < j << 16 >> 16 : 0;
                    g = i ? a : g;
                    h = c + 5 | 0;
                    a = h & 65535;
                    if (a << 16 >> 16 >= 40) break; else {
                        c = h << 16 >> 16;
                        j = i ? e : j
                    }
                }
                b[d + (g << 16 >> 16 << 1) >> 1] = -1;
                f = f + 1 << 16 >> 16
            } while ((f << 16 >> 16 | 0) < (k | 0));
            return
        }

        function rd(a, d, e, f, g, h, j, k) {
            a = a | 0;
            d = d | 0;
            e = e | 0;
            f = f | 0;
            g = g | 0;
            h = h | 0;
            j = j | 0;
            k = k | 0;
            var l = 0, m = 0, n = 0, o = 0, p = 0, q = 0, r = 0, s = 0, t = 0, u = 0, v = 0, w = 0, x = 0, y = 0;
            y = i;
            i = i + 80 | 0;
            x = y;
            p = 40;
            q = d;
            r = a;
            m = 256;
            n = 256;
            while (1) {
                l = b[q >> 1] | 0;
                q = q + 2 | 0;
                l = Z(l, l) | 0;
                if ((l | 0) != 1073741824) {
                    o = (l << 1) + m | 0;
                    if ((l ^ m | 0) > 0 & (o ^ m | 0) < 0) {
                        c[k >> 2] = 1;
                        m = (m >>> 31) + 2147483647 | 0
                    } else m = o
                } else {
                    c[k >> 2] = 1;
                    m = 2147483647
                }
                w = b[r >> 1] | 0;
                n = (Z(w << 1, w) | 0) + n | 0;
                p = p + -1 << 16 >> 16;
                if (!(p << 16 >> 16)) break; else r = r + 2 | 0
            }
            w = ce(m, k) | 0;
            u = w << 5;
            w = ((u >> 5 | 0) == (w | 0) ? u : w >> 31 ^ 2147418112) >> 16;
            u = (ce(n, k) | 0) << 5 >> 16;
            v = 39;
            s = d + 78 | 0;
            t = x + 78 | 0;
            l = e + 78 | 0;
            while (1) {
                r = Z(b[s >> 1] | 0, w) | 0;
                s = s + -2 | 0;
                q = r << 1;
                d = a + (v << 1) | 0;
                m = b[d >> 1] | 0;
                p = Z(m << 16 >> 16, u) | 0;
                if ((p | 0) != 1073741824) {
                    o = (p << 1) + q | 0;
                    if ((p ^ q | 0) > 0 & (o ^ q | 0) < 0) {
                        c[k >> 2] = 1;
                        o = (r >>> 30 & 1) + 2147483647 | 0
                    }
                } else {
                    c[k >> 2] = 1;
                    o = 2147483647
                }
                n = o << 10;
                n = Ce((n >> 10 | 0) == (o | 0) ? n : o >> 31 ^ 2147483647, k) | 0;
                if (n << 16 >> 16 > -1) b[l >> 1] = 32767; else {
                    b[l >> 1] = -32767;
                    if (n << 16 >> 16 == -32768) n = 32767; else n = 0 - (n & 65535) & 65535;
                    if (m << 16 >> 16 == -32768) o = 32767; else o = 0 - (m & 65535) & 65535;
                    b[d >> 1] = o
                }
                l = l + -2 | 0;
                b[t >> 1] = n;
                if ((v | 0) <= 0) break; else {
                    v = v + -1 | 0;
                    t = t + -2 | 0
                }
            }
            d = g << 16 >> 16;
            if (g << 16 >> 16 <= 0) {
                b[h + (d << 1) >> 1] = b[h >> 1] | 0;
                i = y;
                return
            }
            r = j & 65535;
            q = 0;
            p = -1;
            l = 0;
            while (1) {
                if ((q | 0) < 40) {
                    n = q;
                    o = q & 65535;
                    m = -1;
                    while (1) {
                        k = b[x + (n << 1) >> 1] | 0;
                        j = k << 16 >> 16 > m << 16 >> 16;
                        m = j ? k : m;
                        l = j ? o : l;
                        n = n + r | 0;
                        o = n & 65535;
                        if (o << 16 >> 16 >= 40) break; else n = n << 16 >> 16
                    }
                } else m = -1;
                b[f + (q << 1) >> 1] = l;
                if (m << 16 >> 16 > p << 16 >> 16) b[h >> 1] = q; else m = p;
                q = q + 1 | 0;
                if ((q & 65535) << 16 >> 16 == g << 16 >> 16) break; else p = m
            }
            l = b[h >> 1] | 0;
            b[h + (d << 1) >> 1] = l;
            if (g << 16 >> 16 > 1) m = 1; else {
                i = y;
                return
            }
            do {
                f = l + 1 << 16 >> 16;
                l = f << 16 >> 16 >= g << 16 >> 16 ? 0 : f;
                b[h + (m << 1) >> 1] = l;
                b[h + (m + d << 1) >> 1] = l;
                m = m + 1 | 0
            } while ((m & 65535) << 16 >> 16 != g << 16 >> 16);
            i = y;
            return
        }

        function sd(a) {
            a = a | 0;
            var d = 0;
            if (!a) {
                a = -1;
                return a | 0
            }
            c[a >> 2] = 0;
            d = Je(12) | 0;
            if (!d) {
                a = -1;
                return a | 0
            }
            b[d >> 1] = 8;
            c[a >> 2] = d;
            b[d + 2 >> 1] = 3;
            b[d + 4 >> 1] = 0;
            c[d + 8 >> 2] = 0;
            a = 0;
            return a | 0
        }

        function td(a) {
            a = a | 0;
            var b = 0;
            if (!a) return;
            b = c[a >> 2] | 0;
            if (!b) return;
            Ke(b);
            c[a >> 2] = 0;
            return
        }

        function ud(a, d, e) {
            a = a | 0;
            d = d | 0;
            e = e | 0;
            var f = 0, g = 0, h = 0;
            do if ((d | 0) == 8) {
                _abort();//fix cc 精简
            } else {
                b[a + 2 >> 1] = b[a >> 1] | 0;
                c[e >> 2] = 0;
                d = a + 8 | 0
            } while (0);
            c[d >> 2] = c[e >> 2];
            return
        }

        function vd(a, b, d) {
            a = a | 0;
            b = b | 0;
            d = d | 0;
            var e = 0, f = 0, g = 0;
            if (!a) {
                a = -1;
                return a | 0
            }
            c[a >> 2] = 0;
            d = Je(12) | 0;
            e = d;
            if (!d) {
                a = -1;
                return a | 0
            }
            c[d >> 2] = 0;
            f = d + 4 | 0;
            c[f >> 2] = 0;
            g = d + 8 | 0;
            c[g >> 2] = b;
            if ((dd(d) | 0) << 16 >> 16 == 0 ? (ac(f, c[g >> 2] | 0) | 0) << 16 >> 16 == 0 : 0) {
                ed(c[d >> 2] | 0) | 0;
                cc(c[f >> 2] | 0) | 0;
                c[a >> 2] = e;
                a = 0;
                return a | 0
            }
            fd(d);
            bc(f);
            Ke(d);
            a = -1;
            return a | 0
        }

        function wd(a) {
            a = a | 0;
            var b = 0;
            if (!a) return;
            b = c[a >> 2] | 0;
            if (!b) return;
            fd(b);
            bc((c[a >> 2] | 0) + 4 | 0);
            Ke(c[a >> 2] | 0);
            c[a >> 2] = 0;
            return
        }

        function xd(a, d, f, g, h) {
            a = a | 0;
            d = d | 0;
            f = f | 0;
            g = g | 0;
            h = h | 0;
            var j = 0, k = 0, l = 0, m = 0, n = 0;
            m = i;
            i = i + 448 | 0;
            k = m + 320 | 0;
            l = m;
            Qe(g | 0, 0, 488) | 0;
            j = 0;
            do {
                n = f + (j << 1) | 0;
                b[n >> 1] = (e[n >> 1] | 0) & 65528;
                j = j + 1 | 0
            } while ((j | 0) != 160);
            gd(c[a >> 2] | 0, f, 160);
            n = a + 4 | 0;
            dc(c[n >> 2] | 0, d, f, k, h, l) | 0;
            hd(c[h >> 2] | 0, k, g, (c[n >> 2] | 0) + 2392 | 0);
            i = m;
            return
        }

        function yd(a, c, d, e, f, g, h, j, k, l, m, n, o, p, q, r) {
            a = a | 0;
            c = c | 0;
            d = d | 0;
            e = e | 0;
            f = f | 0;
            g = g | 0;
            h = h | 0;
            j = j | 0;
            k = k | 0;
            l = l | 0;
            m = m | 0;
            n = n | 0;
            o = o | 0;
            p = p | 0;
            q = q | 0;
            r = r | 0;
            var s = 0, t = 0, u = 0;
            u = i;
            i = i + 48 | 0;
            s = u + 22 | 0;
            t = u;
            Ie(f, (a & -2 | 0) == 6 ? d : c, s);
            Ie(f, e, t);
            d = m;
            c = s;
            f = d + 22 | 0;
            do {
                b[d >> 1] = b[c >> 1] | 0;
                d = d + 2 | 0;
                c = c + 2 | 0
            } while ((d | 0) < (f | 0));
            He(g, m, o, 40, l, 0);
            He(t, o, o, 40, l, 0);
            Be(g, h, q, 40);
            d = n;
            c = q;
            f = d + 80 | 0;
            do {
                b[d >> 1] = b[c >> 1] | 0;
                d = d + 2 | 0;
                c = c + 2 | 0
            } while ((d | 0) < (f | 0));
            He(g, n, r, 40, j, 0);
            Be(s, r, p, 40);
            He(t, p, p, 40, k, 0);
            i = u;
            return
        }

        function zd(a, c, d, f, g, h, i, j, k, l, m, n, o, p, q, r, s) {
            a = a | 0;
            c = c | 0;
            d = d | 0;
            f = f | 0;
            g = g | 0;
            h = h | 0;
            i = i | 0;
            j = j | 0;
            k = k | 0;
            l = l | 0;
            m = m | 0;
            n = n | 0;
            o = o | 0;
            p = p | 0;
            q = q | 0;
            r = r | 0;
            s = s | 0;
            var t = 0, u = 0, v = 0, w = 0, x = 0;
            if ((c | 0) == 7) {
                v = 11;
                c = f << 16 >> 16 >>> 1 & 65535;
                t = 2
            } else {
                v = 13;
                c = f;
                t = 1
            }
            b[r >> 1] = f << 16 >> 16 < 13017 ? f : 13017;
            u = d << 16 >> 16;
            q = q + (u << 1) | 0;
            r = c << 16 >> 16;
            g = g << 16 >> 16;
            d = 20;
            c = k;
            s = q;
            while (1) {
                k = s + 2 | 0;
                x = Z(b[s >> 1] | 0, r) | 0;
                w = Z(b[k >> 1] | 0, r) | 0;
                x = (Z(b[c >> 1] | 0, g) | 0) + x << 1;
                w = (Z(b[c + 2 >> 1] | 0, g) | 0) + w << 1 << t;
                b[s >> 1] = ((x << t) + 32768 | 0) >>> 16;
                b[k >> 1] = (w + 32768 | 0) >>> 16;
                d = d + -1 << 16 >> 16;
                if (!(d << 16 >> 16)) break; else {
                    c = c + 4 | 0;
                    s = s + 4 | 0
                }
            }
            c = f << 16 >> 16;
            He(h, q, i + (u << 1) | 0, 40, n, 1);
            d = 30;
            s = 0;
            while (1) {
                w = d + u | 0;
                b[o + (s << 1) >> 1] = (e[a + (w << 1) >> 1] | 0) - (e[i + (w << 1) >> 1] | 0);
                w = Z(b[l + (d << 1) >> 1] | 0, c) | 0;
                x = (Z(b[m + (d << 1) >> 1] | 0, g) | 0) >> v;
                b[p + (s << 1) >> 1] = (e[j + (d << 1) >> 1] | 0) - (w >>> 14) - x;
                s = s + 1 | 0;
                if ((s | 0) == 10) break; else d = d + 1 | 0
            }
            return
        }

        function Ad(a) {
            a = a | 0;
            var d = 0;
            if (!a) {
                a = -1;
                return a | 0
            }
            c[a >> 2] = 0;
            d = Je(16) | 0;
            if (!d) {
                a = -1;
                return a | 0
            }
            ;b[d >> 1] = 0;
            b[d + 2 >> 1] = 0;
            b[d + 4 >> 1] = 0;
            b[d + 6 >> 1] = 0;
            b[d + 8 >> 1] = 0;
            b[d + 10 >> 1] = 0;
            b[d + 12 >> 1] = 0;
            b[d + 14 >> 1] = 0;
            c[a >> 2] = d;
            a = 0;
            return a | 0
        }

        function Bd(a) {
            a = a | 0;
            if (!a) {
                a = -1;
                return a | 0
            }
            ;b[a >> 1] = 0;
            b[a + 2 >> 1] = 0;
            b[a + 4 >> 1] = 0;
            b[a + 6 >> 1] = 0;
            b[a + 8 >> 1] = 0;
            b[a + 10 >> 1] = 0;
            b[a + 12 >> 1] = 0;
            b[a + 14 >> 1] = 0;
            a = 0;
            return a | 0
        }

        function Cd(a) {
            a = a | 0;
            var b = 0;
            if (!a) return;
            b = c[a >> 2] | 0;
            if (!b) return;
            Ke(b);
            c[a >> 2] = 0;
            return
        }

        function Dd(a, c, d) {
            a = a | 0;
            c = c | 0;
            d = d | 0;
            var f = 0, g = 0, h = 0, i = 0;
            f = e[c + 6 >> 1] | 0;
            d = e[c + 8 >> 1] | 0;
            g = f - d | 0;
            g = (g & 65535 | 0) != 32767 ? g & 65535 : 32767;
            h = e[c + 10 >> 1] | 0;
            d = d - h | 0;
            g = (d << 16 >> 16 | 0) < (g << 16 >> 16 | 0) ? d & 65535 : g;
            d = e[c + 12 >> 1] | 0;
            h = h - d | 0;
            g = (h << 16 >> 16 | 0) < (g << 16 >> 16 | 0) ? h & 65535 : g;
            h = e[c + 14 >> 1] | 0;
            d = d - h | 0;
            g = (d << 16 >> 16 | 0) < (g << 16 >> 16 | 0) ? d & 65535 : g;
            h = h - (e[c + 16 >> 1] | 0) | 0;
            d = b[c + 2 >> 1] | 0;
            i = e[c + 4 >> 1] | 0;
            c = (d & 65535) - i | 0;
            c = (c & 65535 | 0) != 32767 ? c & 65535 : 32767;
            f = i - f | 0;
            if (((h << 16 >> 16 | 0) < (g << 16 >> 16 | 0) ? h & 65535 : g) << 16 >> 16 < 1500 ? 1 : (((f << 16 >> 16 | 0) < (c << 16 >> 16 | 0) ? f & 65535 : c) << 16 >> 16 | 0) < ((d << 16 >> 16 > 32e3 ? 600 : d << 16 >> 16 > 30500 ? 800 : 1100) | 0)) {
                h = (b[a >> 1] | 0) + 1 << 16 >> 16;
                i = h << 16 >> 16 > 11;
                b[a >> 1] = i ? 12 : h;
                return i & 1 | 0
            } else {
                b[a >> 1] = 0;
                return 0
            }
            return 0
        }

        function Ed(a, c, d) {
            a = a | 0;
            c = c | 0;
            d = d | 0;
            c = De(c, 3, d) | 0;
            c = Rd(c, b[a + 2 >> 1] | 0, d) | 0;
            c = Rd(c, b[a + 4 >> 1] | 0, d) | 0;
            c = Rd(c, b[a + 6 >> 1] | 0, d) | 0;
            c = Rd(c, b[a + 8 >> 1] | 0, d) | 0;
            c = Rd(c, b[a + 10 >> 1] | 0, d) | 0;
            c = Rd(c, b[a + 12 >> 1] | 0, d) | 0;
            return (Rd(c, b[a + 14 >> 1] | 0, d) | 0) << 16 >> 16 > 15565 | 0
        }

        function Fd(a, c, d) {
            a = a | 0;
            c = c | 0;
            d = d | 0;
            var e = 0;
            d = a + 4 | 0;
            b[a + 2 >> 1] = b[d >> 1] | 0;
            e = a + 6 | 0;
            b[d >> 1] = b[e >> 1] | 0;
            d = a + 8 | 0;
            b[e >> 1] = b[d >> 1] | 0;
            e = a + 10 | 0;
            b[d >> 1] = b[e >> 1] | 0;
            d = a + 12 | 0;
            b[e >> 1] = b[d >> 1] | 0;
            a = a + 14 | 0;
            b[d >> 1] = b[a >> 1] | 0;
            b[a >> 1] = c << 16 >> 16 >>> 3;
            return
        }

        function Gd(a) {
            a = a | 0;
            var d = 0, e = 0, f = 0;
            if (!a) {
                f = -1;
                return f | 0
            }
            c[a >> 2] = 0;
            d = Je(128) | 0;
            if (!d) {
                f = -1;
                return f | 0
            }
            e = d + 72 | 0;
            f = e + 46 | 0;
            do {
                b[e >> 1] = 0;
                e = e + 2 | 0
            } while ((e | 0) < (f | 0));
            b[d >> 1] = 150;
            b[d + 36 >> 1] = 150;
            b[d + 18 >> 1] = 150;
            b[d + 54 >> 1] = 0;
            b[d + 2 >> 1] = 150;
            b[d + 38 >> 1] = 150;
            b[d + 20 >> 1] = 150;
            b[d + 56 >> 1] = 0;
            b[d + 4 >> 1] = 150;
            b[d + 40 >> 1] = 150;
            b[d + 22 >> 1] = 150;
            b[d + 58 >> 1] = 0;
            b[d + 6 >> 1] = 150;
            b[d + 42 >> 1] = 150;
            b[d + 24 >> 1] = 150;
            b[d + 60 >> 1] = 0;
            b[d + 8 >> 1] = 150;
            b[d + 44 >> 1] = 150;
            b[d + 26 >> 1] = 150;
            b[d + 62 >> 1] = 0;
            b[d + 10 >> 1] = 150;
            b[d + 46 >> 1] = 150;
            b[d + 28 >> 1] = 150;
            b[d + 64 >> 1] = 0;
            b[d + 12 >> 1] = 150;
            b[d + 48 >> 1] = 150;
            b[d + 30 >> 1] = 150;
            b[d + 66 >> 1] = 0;
            b[d + 14 >> 1] = 150;
            b[d + 50 >> 1] = 150;
            b[d + 32 >> 1] = 150;
            b[d + 68 >> 1] = 0;
            b[d + 16 >> 1] = 150;
            b[d + 52 >> 1] = 150;
            b[d + 34 >> 1] = 150;
            b[d + 70 >> 1] = 0;
            b[d + 118 >> 1] = 13106;
            b[d + 120 >> 1] = 0;
            b[d + 122 >> 1] = 0;
            b[d + 124 >> 1] = 0;
            b[d + 126 >> 1] = 13106;
            c[a >> 2] = d;
            f = 0;
            return f | 0
        }

        function Hd(a) {
            a = a | 0;
            var c = 0, d = 0;
            if (!a) {
                d = -1;
                return d | 0
            }
            c = a + 72 | 0;
            d = c + 46 | 0;
            do {
                b[c >> 1] = 0;
                c = c + 2 | 0
            } while ((c | 0) < (d | 0));
            b[a >> 1] = 150;
            b[a + 36 >> 1] = 150;
            b[a + 18 >> 1] = 150;
            b[a + 54 >> 1] = 0;
            b[a + 2 >> 1] = 150;
            b[a + 38 >> 1] = 150;
            b[a + 20 >> 1] = 150;
            b[a + 56 >> 1] = 0;
            b[a + 4 >> 1] = 150;
            b[a + 40 >> 1] = 150;
            b[a + 22 >> 1] = 150;
            b[a + 58 >> 1] = 0;
            b[a + 6 >> 1] = 150;
            b[a + 42 >> 1] = 150;
            b[a + 24 >> 1] = 150;
            b[a + 60 >> 1] = 0;
            b[a + 8 >> 1] = 150;
            b[a + 44 >> 1] = 150;
            b[a + 26 >> 1] = 150;
            b[a + 62 >> 1] = 0;
            b[a + 10 >> 1] = 150;
            b[a + 46 >> 1] = 150;
            b[a + 28 >> 1] = 150;
            b[a + 64 >> 1] = 0;
            b[a + 12 >> 1] = 150;
            b[a + 48 >> 1] = 150;
            b[a + 30 >> 1] = 150;
            b[a + 66 >> 1] = 0;
            b[a + 14 >> 1] = 150;
            b[a + 50 >> 1] = 150;
            b[a + 32 >> 1] = 150;
            b[a + 68 >> 1] = 0;
            b[a + 16 >> 1] = 150;
            b[a + 52 >> 1] = 150;
            b[a + 34 >> 1] = 150;
            b[a + 70 >> 1] = 0;
            b[a + 118 >> 1] = 13106;
            b[a + 120 >> 1] = 0;
            b[a + 122 >> 1] = 0;
            b[a + 124 >> 1] = 0;
            b[a + 126 >> 1] = 13106;
            d = 0;
            return d | 0
        }

        function Id(a) {
            a = a | 0;
            var b = 0;
            if (!a) return;
            b = c[a >> 2] | 0;
            if (!b) return;
            Ke(b);
            c[a >> 2] = 0;
            return
        }

        //fix cc 精简

        function Rd(a, b, d) {
            a = a | 0;
            b = b | 0;
            d = d | 0;
            a = (b << 16 >> 16) + (a << 16 >> 16) | 0;
            if ((a | 0) <= 32767) {
                if ((a | 0) < -32768) {
                    c[d >> 2] = 1;
                    a = -32768
                }
            } else {
                c[d >> 2] = 1;
                a = 32767
            }
            return a & 65535 | 0
        }

        function Sd(a, c, d, e) {
            a = a | 0;
            c = c | 0;
            d = d | 0;
            e = e | 0;
            var f = 0, g = 0, h = 0, j = 0, k = 0, l = 0, m = 0, n = 0, o = 0, p = 0, q = 0, r = 0, s = 0, t = 0, u = 0,
                v = 0, w = 0, x = 0, y = 0, z = 0, A = 0, B = 0;
            y = i;
            i = i + 32 | 0;
            w = y + 12 | 0;
            x = y;
            b[w >> 1] = 1024;
            b[x >> 1] = 1024;
            k = b[a + 2 >> 1] | 0;
            h = b[a + 20 >> 1] | 0;
            e = ((h + k | 0) >>> 2) + 64512 | 0;
            b[w + 2 >> 1] = e;
            h = ((k - h | 0) >>> 2) + 1024 | 0;
            b[x + 2 >> 1] = h;
            k = b[a + 4 >> 1] | 0;
            f = b[a + 18 >> 1] | 0;
            e = ((f + k | 0) >>> 2) - e | 0;
            b[w + 4 >> 1] = e;
            h = ((k - f | 0) >>> 2) + h | 0;
            b[x + 4 >> 1] = h;
            f = b[a + 6 >> 1] | 0;
            k = b[a + 16 >> 1] | 0;
            e = ((k + f | 0) >>> 2) - e | 0;
            b[w + 6 >> 1] = e;
            h = ((f - k | 0) >>> 2) + h | 0;
            b[x + 6 >> 1] = h;
            k = b[a + 8 >> 1] | 0;
            f = b[a + 14 >> 1] | 0;
            e = ((f + k | 0) >>> 2) - e | 0;
            b[w + 8 >> 1] = e;
            h = ((k - f | 0) >>> 2) + h | 0;
            b[x + 8 >> 1] = h;
            f = b[a + 10 >> 1] | 0;
            k = b[a + 12 >> 1] | 0;
            e = ((k + f | 0) >>> 2) - e | 0;
            b[w + 10 >> 1] = e;
            b[x + 10 >> 1] = ((f - k | 0) >>> 2) + h;
            h = b[3454] | 0;
            k = h << 16 >> 16;
            a = b[w + 2 >> 1] | 0;
            f = (a << 16 >> 16 << 14) + (k << 10) | 0;
            s = f & -65536;
            f = (f >>> 1) - (f >> 16 << 15) << 16;
            v = (((Z(f >> 16, k) | 0) >> 15) + (Z(s >> 16, k) | 0) << 2) + -16777216 | 0;
            v = (b[w + 4 >> 1] << 14) + v | 0;
            j = v >> 16;
            v = (v >>> 1) - (j << 15) << 16;
            s = (((Z(v >> 16, k) | 0) >> 15) + (Z(j, k) | 0) << 2) - ((f >> 15) + s) | 0;
            s = (b[w + 6 >> 1] << 14) + s | 0;
            f = s >> 16;
            s = (s >>> 1) - (f << 15) << 16;
            j = (((Z(s >> 16, k) | 0) >> 15) + (Z(f, k) | 0) << 2) - ((v >> 15) + (j << 16)) | 0;
            j = (b[w + 8 >> 1] << 14) + j | 0;
            v = j >> 16;
            f = (e << 16 >> 3) + ((((Z((j >>> 1) - (v << 15) << 16 >> 16, k) | 0) >> 15) + (Z(v, k) | 0) << 1) - ((s >> 15) + (f << 16))) | 0;
            s = w + 4 | 0;
            k = w;
            v = 0;
            j = 0;
            e = 0;
            r = w + 10 | 0;
            f = (f + 33554432 | 0) >>> 0 < 67108863 ? f >>> 10 & 65535 : (f | 0) > 33554431 ? 32767 : -32768;
            a:while (1) {
                t = a << 16 >> 16 << 14;
                q = k + 6 | 0;
                p = k + 8 | 0;
                o = j << 16 >> 16;
                while (1) {
                    if ((o | 0) >= 60) break a;
                    k = (o & 65535) + 1 << 16 >> 16;
                    l = b[6908 + (k << 16 >> 16 << 1) >> 1] | 0;
                    u = l << 16 >> 16;
                    j = t + (u << 10) | 0;
                    g = j & -65536;
                    j = (j >>> 1) - (j >> 16 << 15) << 16;
                    m = (((Z(j >> 16, u) | 0) >> 15) + (Z(g >> 16, u) | 0) << 2) + -16777216 | 0;
                    n = b[s >> 1] | 0;
                    m = (n << 16 >> 16 << 14) + m | 0;
                    B = m >> 16;
                    m = (m >>> 1) - (B << 15) << 16;
                    g = (((Z(m >> 16, u) | 0) >> 15) + (Z(B, u) | 0) << 2) - ((j >> 15) + g) | 0;
                    j = b[q >> 1] | 0;
                    g = (j << 16 >> 16 << 14) + g | 0;
                    a = g >> 16;
                    g = (g >>> 1) - (a << 15) << 16;
                    B = (((Z(g >> 16, u) | 0) >> 15) + (Z(a, u) | 0) << 2) - ((m >> 15) + (B << 16)) | 0;
                    m = b[p >> 1] | 0;
                    B = (m << 16 >> 16 << 14) + B | 0;
                    A = B >> 16;
                    a = (((Z((B >>> 1) - (A << 15) << 16 >> 16, u) | 0) >> 15) + (Z(A, u) | 0) << 1) - ((g >> 15) + (a << 16)) | 0;
                    g = b[r >> 1] | 0;
                    a = (g << 16 >> 16 << 13) + a | 0;
                    a = (a + 33554432 | 0) >>> 0 < 67108863 ? a >>> 10 & 65535 : (a | 0) > 33554431 ? 32767 : -32768;
                    if ((Z(a << 16 >> 16, f << 16 >> 16) | 0) < 1) {
                        u = k;
                        k = n;
                        break
                    } else {
                        o = o + 1 | 0;
                        h = l;
                        f = a
                    }
                }
                s = g << 16 >> 16 << 13;
                r = k << 16 >> 16 << 14;
                n = j << 16 >> 16 << 14;
                p = m << 16 >> 16 << 14;
                g = l << 16 >> 16;
                o = 4;
                while (1) {
                    A = (h << 16 >> 16 >>> 1) + (g >>> 1) | 0;
                    g = A << 16;
                    q = g >> 16;
                    g = t + (g >> 6) | 0;
                    B = g & -65536;
                    g = (g >>> 1) - (g >> 16 << 15) << 16;
                    m = r + ((((Z(g >> 16, q) | 0) >> 15) + (Z(B >> 16, q) | 0) << 2) + -16777216) | 0;
                    k = m >> 16;
                    m = (m >>> 1) - (k << 15) << 16;
                    B = n + ((((Z(m >> 16, q) | 0) >> 15) + (Z(k, q) | 0) << 2) - ((g >> 15) + B)) | 0;
                    g = B >> 16;
                    B = (B >>> 1) - (g << 15) << 16;
                    k = p + ((((Z(B >> 16, q) | 0) >> 15) + (Z(g, q) | 0) << 2) - ((m >> 15) + (k << 16))) | 0;
                    m = k >> 16;
                    A = A & 65535;
                    g = s + ((((Z((k >>> 1) - (m << 15) << 16 >> 16, q) | 0) >> 15) + (Z(m, q) | 0) << 1) - ((B >> 15) + (g << 16))) | 0;
                    g = (g + 33554432 | 0) >>> 0 < 67108863 ? g >>> 10 & 65535 : (g | 0) > 33554431 ? 32767 : -32768;
                    B = (Z(g << 16 >> 16, a << 16 >> 16) | 0) < 1;
                    q = B ? l : A;
                    a = B ? a : g;
                    h = B ? A : h;
                    f = B ? g : f;
                    o = o + -1 << 16 >> 16;
                    g = q << 16 >> 16;
                    if (!(o << 16 >> 16)) {
                        l = g;
                        j = h;
                        h = q;
                        break
                    } else l = q
                }
                k = e << 16 >> 16;
                g = a << 16 >> 16;
                a = (f & 65535) - g | 0;
                f = a << 16;
                if (f) {
                    B = (a & 65535) - (a >>> 15 & 1) | 0;
                    B = B << 16 >> 31 ^ B;
                    a = (qe(B & 65535) | 0) << 16 >> 16;
                    a = (Z((Td(16383, B << 16 >> 16 << a & 65535) | 0) << 16 >> 16, (j & 65535) - l << 16 >> 16) | 0) >> 19 - a;
                    if ((f | 0) < 0) a = 0 - (a << 16 >> 16) | 0;
                    h = l - ((Z(a << 16 >> 16, g) | 0) >>> 10) & 65535
                }
                b[c + (k << 1) >> 1] = h;
                f = v << 16 >> 16 == 0 ? x : w;
                A = h << 16 >> 16;
                a = b[f + 2 >> 1] | 0;
                g = (a << 16 >> 16 << 14) + (A << 10) | 0;
                B = g & -65536;
                g = (g >>> 1) - (g >> 16 << 15) << 16;
                t = (((Z(g >> 16, A) | 0) >> 15) + (Z(B >> 16, A) | 0) << 2) + -16777216 | 0;
                t = (b[f + 4 >> 1] << 14) + t | 0;
                s = t >> 16;
                t = (t >>> 1) - (s << 15) << 16;
                B = (((Z(t >> 16, A) | 0) >> 15) + (Z(s, A) | 0) << 2) - ((g >> 15) + B) | 0;
                B = (b[f + 6 >> 1] << 14) + B | 0;
                g = B >> 16;
                B = (B >>> 1) - (g << 15) << 16;
                s = (((Z(B >> 16, A) | 0) >> 15) + (Z(g, A) | 0) << 2) - ((t >> 15) + (s << 16)) | 0;
                s = (b[f + 8 >> 1] << 14) + s | 0;
                t = s >> 16;
                e = e + 1 << 16 >> 16;
                g = (((Z((s >>> 1) - (t << 15) << 16 >> 16, A) | 0) >> 15) + (Z(t, A) | 0) << 1) - ((B >> 15) + (g << 16)) | 0;
                g = (b[f + 10 >> 1] << 13) + g | 0;
                if (e << 16 >> 16 < 10) {
                    s = f + 4 | 0;
                    k = f;
                    v = v ^ 1;
                    j = u;
                    r = f + 10 | 0;
                    f = (g + 33554432 | 0) >>> 0 < 67108863 ? g >>> 10 & 65535 : (g | 0) > 33554431 ? 32767 : -32768
                } else {
                    z = 13;
                    break
                }
            }
            if ((z | 0) == 13) {
                i = y;
                return
            }
            b[c >> 1] = b[d >> 1] | 0;
            b[c + 2 >> 1] = b[d + 2 >> 1] | 0;
            b[c + 4 >> 1] = b[d + 4 >> 1] | 0;
            b[c + 6 >> 1] = b[d + 6 >> 1] | 0;
            b[c + 8 >> 1] = b[d + 8 >> 1] | 0;
            b[c + 10 >> 1] = b[d + 10 >> 1] | 0;
            b[c + 12 >> 1] = b[d + 12 >> 1] | 0;
            b[c + 14 >> 1] = b[d + 14 >> 1] | 0;
            b[c + 16 >> 1] = b[d + 16 >> 1] | 0;
            b[c + 18 >> 1] = b[d + 18 >> 1] | 0;
            i = y;
            return
        }

        function Td(a, b) {
            a = a | 0;
            b = b | 0;
            var c = 0, d = 0, e = 0, f = 0, g = 0, h = 0;
            e = b << 16 >> 16;
            if (a << 16 >> 16 < 1 ? 1 : a << 16 >> 16 > b << 16 >> 16) {
                e = 0;
                return e | 0
            }
            if (a << 16 >> 16 == b << 16 >> 16) {
                e = 32767;
                return e | 0
            }
            d = e << 1;
            c = e << 2;
            f = a << 16 >> 16 << 3;
            a = (f | 0) < (c | 0);
            f = f - (a ? 0 : c) | 0;
            a = a ? 0 : 4;
            g = (f | 0) < (d | 0);
            f = f - (g ? 0 : d) | 0;
            b = (f | 0) < (e | 0);
            a = (b & 1 | (g ? a : a | 2)) << 3 ^ 8;
            b = f - (b ? 0 : e) << 3;
            if ((b | 0) >= (c | 0)) {
                b = b - c | 0;
                a = a & 65528 | 4
            }
            f = (b | 0) < (d | 0);
            g = b - (f ? 0 : d) | 0;
            b = (g | 0) < (e | 0);
            a = (b & 1 ^ 1 | (f ? a : a | 2)) << 16 >> 13;
            b = g - (b ? 0 : e) << 3;
            if ((b | 0) >= (c | 0)) {
                b = b - c | 0;
                a = a & 65528 | 4
            }
            f = (b | 0) < (d | 0);
            g = b - (f ? 0 : d) | 0;
            b = (g | 0) < (e | 0);
            a = (b & 1 ^ 1 | (f ? a : a | 2)) << 16 >> 13;
            b = g - (b ? 0 : e) << 3;

            if ((b | 0) >= (c | 0)) {
                b = b - c | 0;
                a = a & 65528 | 4
            }
            h = (b | 0) < (d | 0);
            f = b - (h ? 0 : d) | 0;
            g = (f | 0) < (e | 0);
            b = (g & 1 ^ 1 | (h ? a : a | 2)) << 16 >> 13;
            a = f - (g ? 0 : e) << 3;
            if ((a | 0) >= (c | 0)) {
                a = a - c | 0;
                b = b & 65528 | 4
            }
            h = (a | 0) < (d | 0);
            h = ((a - (h ? 0 : d) | 0) >= (e | 0) | (h ? b : b | 2)) & 65535;
            return h | 0
        }

        function Ud(a) {
            a = a | 0;
            if (!a) {
                a = -1;
                return a | 0
            }
            b[a >> 1] = -14336;
            b[a + 8 >> 1] = -2381;
            b[a + 2 >> 1] = -14336;
            b[a + 10 >> 1] = -2381;
            b[a + 4 >> 1] = -14336;
            b[a + 12 >> 1] = -2381;
            b[a + 6 >> 1] = -14336;
            b[a + 14 >> 1] = -2381;
            a = 0;
            return a | 0
        }

        function Vd(a, d, f, g, h, j, k, l) {
            a = a | 0;
            d = d | 0;
            f = f | 0;
            g = g | 0;
            h = h | 0;
            j = j | 0;
            k = k | 0;
            l = l | 0;
            var m = 0, n = 0, o = 0, p = 0, q = 0, r = 0;
            r = i;
            i = i + 16 | 0;
            p = r + 2 | 0;
            q = r;
            m = 0;
            n = 10;
            while (1) {
                o = b[f >> 1] | 0;
                o = ((Z(o, o) | 0) >>> 3) + m | 0;
                m = b[f + 2 >> 1] | 0;
                m = o + ((Z(m, m) | 0) >>> 3) | 0;
                o = b[f + 4 >> 1] | 0;
                o = m + ((Z(o, o) | 0) >>> 3) | 0;
                m = b[f + 6 >> 1] | 0;
                m = o + ((Z(m, m) | 0) >>> 3) | 0;
                n = n + -1 << 16 >> 16;
                if (!(n << 16 >> 16)) break; else f = f + 8 | 0
            }
            n = m << 4;
            n = (n | 0) < 0 ? 2147483647 : n;
            if ((d | 0) == 7) {
                de(((Ce(n, l) | 0) << 16 >> 16) * 52428 | 0, p, q, l);
                o = e[p >> 1] << 16;
                n = b[q >> 1] << 1;
                d = b[a + 8 >> 1] | 0;
                m = (d << 16 >> 16) * 88 | 0;
                if (d << 16 >> 16 > -1 & (m | 0) < -783741) {
                    c[l >> 2] = 1;
                    f = 2147483647
                } else f = m + 783741 | 0;
                d = (b[a + 10 >> 1] | 0) * 74 | 0;
                m = d + f | 0;
                if ((d ^ f | 0) > -1 & (m ^ f | 0) < 0) {
                    c[l >> 2] = 1;
                    f = (f >>> 31) + 2147483647 | 0
                } else f = m;
                d = (b[a + 12 >> 1] | 0) * 44 | 0;
                m = d + f | 0;
                if ((d ^ f | 0) > -1 & (m ^ f | 0) < 0) {
                    c[l >> 2] = 1;
                    f = (f >>> 31) + 2147483647 | 0
                } else f = m;
                a = (b[a + 14 >> 1] | 0) * 24 | 0;
                m = a + f | 0;
                if ((a ^ f | 0) > -1 & (m ^ f | 0) < 0) {
                    c[l >> 2] = 1;
                    m = (f >>> 31) + 2147483647 | 0
                }
                a = o + -1966080 + n | 0;
                f = m - a | 0;
                if (((f ^ m) & (m ^ a) | 0) < 0) {
                    c[l >> 2] = 1;
                    f = (m >>> 31) + 2147483647 | 0
                }
                l = f >> 17;
                b[g >> 1] = l;
                l = (f >> 2) - (l << 15) | 0;
                l = l & 65535;
                b[h >> 1] = l;
                i = r;
                return
            }
            o = pe(n) | 0;
            m = o << 16 >> 16;
            if (o << 16 >> 16 > 0) {
                f = n << m;
                if ((f >> m | 0) == (n | 0)) n = f; else n = n >> 31 ^ 2147483647
            } else {
                m = 0 - m << 16;
                if ((m | 0) < 2031616) n = n >> (m >> 16); else n = 0
            }
            ee(n, o, p, q);
            p = Z(b[p >> 1] | 0, -49320) | 0;
            m = (Z(b[q >> 1] | 0, -24660) | 0) >> 15;
            m = (m & 65536 | 0) == 0 ? m : m | -65536;
            q = m << 1;
            f = q + p | 0;
            if ((q ^ p | 0) > -1 & (f ^ q | 0) < 0) {
                c[l >> 2] = 1;
                f = (m >>> 30 & 1) + 2147483647 | 0
            }
            switch (d | 0) {
                case 6: {
                    m = f + 2134784 | 0;
                    if ((f | 0) > -1 & (m ^ f | 0) < 0) {
                        c[l >> 2] = 1;
                        m = (f >>> 31) + 2147483647 | 0
                    }
                    break
                }
                case 5: {
                    b[k >> 1] = n >>> 16;
                    b[j >> 1] = -11 - (o & 65535);
                    m = f + 2183936 | 0;
                    if ((f | 0) > -1 & (m ^ f | 0) < 0) {
                        c[l >> 2] = 1;
                        m = (f >>> 31) + 2147483647 | 0
                    }
                    break
                }
                case 4: {
                    m = f + 2085632 | 0;
                    if ((f | 0) > -1 & (m ^ f | 0) < 0) {
                        c[l >> 2] = 1;
                        m = (f >>> 31) + 2147483647 | 0
                    }
                    break
                }
                case 3: {
                    m = f + 2065152 | 0;
                    if ((f | 0) > -1 & (m ^ f | 0) < 0) {
                        c[l >> 2] = 1;
                        m = (f >>> 31) + 2147483647 | 0
                    }
                    break
                }
                default: {
                    m = f + 2134784 | 0;
                    if ((f | 0) > -1 & (m ^ f | 0) < 0) {
                        c[l >> 2] = 1;
                        m = (f >>> 31) + 2147483647 | 0
                    }
                }
            }
            do if ((m | 0) <= 2097151) if ((m | 0) < -2097152) {
                c[l >> 2] = 1;
                f = -2147483648;
                break
            } else {
                f = m << 10;
                break
            } else {
                c[l >> 2] = 1;
                f = 2147483647
            } while (0);
            k = (b[a >> 1] | 0) * 11142 | 0;
            m = k + f | 0;
            if ((k ^ f | 0) > -1 & (m ^ f | 0) < 0) {
                c[l >> 2] = 1;
                m = (f >>> 31) + 2147483647 | 0
            }
            k = (b[a + 2 >> 1] | 0) * 9502 | 0;
            f = k + m | 0;
            if ((k ^ m | 0) > -1 & (f ^ m | 0) < 0) {
                c[l >> 2] = 1;
                f = (m >>> 31) + 2147483647 | 0
            }
            k = (b[a + 4 >> 1] | 0) * 5570 | 0;
            m = k + f | 0;
            if ((k ^ f | 0) > -1 & (m ^ f | 0) < 0) {
                c[l >> 2] = 1;
                m = (f >>> 31) + 2147483647 | 0
            }
            a = (b[a + 6 >> 1] | 0) * 3112 | 0;
            f = a + m | 0;
            if ((a ^ m | 0) > -1 & (f ^ m | 0) < 0) {
                c[l >> 2] = 1;
                f = (m >>> 31) + 2147483647 | 0
            }
            f = Z(f >> 16, (d | 0) == 4 ? 10878 : 10886) | 0;
            if ((f | 0) < 0) f = ~((f ^ -256) >> 8); else f = f >> 8;
            b[g >> 1] = f >>> 16;
            if ((f | 0) < 0) m = ~((f ^ -2) >> 1); else m = f >> 1;
            g = f >> 16 << 15;
            f = m - g | 0;
            if (((f ^ m) & (g ^ m) | 0) >= 0) {
                l = f;
                l = l & 65535;
                b[h >> 1] = l;
                i = r;
                return
            }
            c[l >> 2] = 1;
            l = (m >>> 31) + 2147483647 | 0;
            l = l & 65535;
            b[h >> 1] = l;
            i = r;
            return
        }

        function Wd(a, c, d) {
            a = a | 0;
            c = c | 0;
            d = d | 0;
            var e = 0, f = 0, g = 0;
            f = a + 4 | 0;
            b[a + 6 >> 1] = b[f >> 1] | 0;
            g = a + 12 | 0;
            b[a + 14 >> 1] = b[g >> 1] | 0;
            e = a + 2 | 0;
            b[f >> 1] = b[e >> 1] | 0;
            f = a + 10 | 0;
            b[g >> 1] = b[f >> 1] | 0;
            b[e >> 1] = b[a >> 1] | 0;
            e = a + 8 | 0;
            b[f >> 1] = b[e >> 1] | 0;
            b[e >> 1] = c;
            b[a >> 1] = d;
            return
        }

        //fix cc 精简

        function Yd(a) {
            a = a | 0;
            c[a >> 2] = 6892;
            c[a + 4 >> 2] = 8180;
            c[a + 8 >> 2] = 21e3;
            c[a + 12 >> 2] = 9716;
            c[a + 16 >> 2] = 22024;
            c[a + 20 >> 2] = 12788;
            c[a + 24 >> 2] = 24072;
            c[a + 28 >> 2] = 26120;
            c[a + 32 >> 2] = 28168;
            c[a + 36 >> 2] = 6876;
            c[a + 40 >> 2] = 7452;
            c[a + 44 >> 2] = 8140;
            c[a + 48 >> 2] = 20980;
            c[a + 52 >> 2] = 16884;
            c[a + 56 >> 2] = 17908;
            c[a + 60 >> 2] = 7980;
            c[a + 64 >> 2] = 8160;
            c[a + 68 >> 2] = 6678;
            c[a + 72 >> 2] = 6646;
            c[a + 76 >> 2] = 6614;
            c[a + 80 >> 2] = 29704;
            c[a + 84 >> 2] = 28680;
            c[a + 88 >> 2] = 3720;
            c[a + 92 >> 2] = 8;
            c[a + 96 >> 2] = 4172;
            c[a + 100 >> 2] = 44;
            c[a + 104 >> 2] = 3436;
            c[a + 108 >> 2] = 30316;
            c[a + 112 >> 2] = 30796;
            c[a + 116 >> 2] = 31276;
            c[a + 120 >> 2] = 7472;
            c[a + 124 >> 2] = 7552;
            c[a + 128 >> 2] = 7632;
            c[a + 132 >> 2] = 7712;
            return
        }

        function Zd(a, c) {
            a = a | 0;
            c = c | 0;
            var d = 0, e = 0, f = 0, g = 0, h = 0, j = 0, k = 0, l = 0, m = 0, n = 0;
            n = i;
            i = i + 48 | 0;
            l = n + 18 | 0;
            m = n;
            k = c << 16 >> 16;
            Oe(m | 0, a | 0, k << 1 | 0) | 0;
            if (c << 16 >> 16 > 0) {
                d = 0;
                e = 0
            } else {
                _abort();//fix cc 精简
            }
            do {
                j = 0;
                h = -32767;
                while (1) {
                    f = b[m + (j << 1) >> 1] | 0;
                    g = f << 16 >> 16 < h << 16 >> 16;
                    e = g ? e : j & 65535;
                    j = j + 1 | 0;
                    if ((j & 65535) << 16 >> 16 == c << 16 >> 16) break; else h = g ? h : f
                }
                b[m + (e << 16 >> 16 << 1) >> 1] = -32768;
                b[l + (d << 1) >> 1] = e;
                d = d + 1 | 0
            } while ((d & 65535) << 16 >> 16 != c << 16 >> 16);
            m = k >> 1;
            m = l + (m << 1) | 0;
            m = b[m >> 1] | 0;
            m = m << 16 >> 16;
            m = a + (m << 1) | 0;
            m = b[m >> 1] | 0;
            i = n;
            return m | 0
        }

        function _d(a, c, d, e, f) {
            a = a | 0;
            c = c | 0;
            d = d | 0;
            e = e | 0;
            f = f | 0;
            var g = 0, h = 0, j = 0, k = 0, l = 0, m = 0, n = 0, o = 0, p = 0, q = 0, r = 0, s = 0, t = 0, u = 0, v = 0,
                w = 0, x = 0, y = 0, z = 0, A = 0;
            g = i;
            i = i + 32 | 0;
            h = g;
            A = c + 2 | 0;
            z = h + 2 | 0;
            b[h >> 1] = ((b[c >> 1] | 0) >>> 1) + ((b[a >> 1] | 0) >>> 1);
            y = c + 4 | 0;
            x = h + 4 | 0;
            b[z >> 1] = ((b[A >> 1] | 0) >>> 1) + ((b[a + 2 >> 1] | 0) >>> 1);
            w = c + 6 | 0;
            v = h + 6 | 0;
            b[x >> 1] = ((b[y >> 1] | 0) >>> 1) + ((b[a + 4 >> 1] | 0) >>> 1);
            u = c + 8 | 0;
            t = h + 8 | 0;
            b[v >> 1] = ((b[w >> 1] | 0) >>> 1) + ((b[a + 6 >> 1] | 0) >>> 1);
            s = c + 10 | 0;
            r = h + 10 | 0;
            b[t >> 1] = ((b[u >> 1] | 0) >>> 1) + ((b[a + 8 >> 1] | 0) >>> 1);
            q = c + 12 | 0;
            p = h + 12 | 0;
            b[r >> 1] = ((b[s >> 1] | 0) >>> 1) + ((b[a + 10 >> 1] | 0) >>> 1);
            o = c + 14 | 0;
            n = h + 14 | 0;
            b[p >> 1] = ((b[q >> 1] | 0) >>> 1) + ((b[a + 12 >> 1] | 0) >>> 1);
            m = c + 16 | 0;
            l = h + 16 | 0;
            b[n >> 1] = ((b[o >> 1] | 0) >>> 1) + ((b[a + 14 >> 1] | 0) >>> 1);
            k = c + 18 | 0;
            j = h + 18 | 0;
            b[l >> 1] = ((b[m >> 1] | 0) >>> 1) + ((b[a + 16 >> 1] | 0) >>> 1);
            b[j >> 1] = ((b[k >> 1] | 0) >>> 1) + ((b[a + 18 >> 1] | 0) >>> 1);
            he(h, e, f);
            he(c, e + 22 | 0, f);
            b[h >> 1] = ((b[d >> 1] | 0) >>> 1) + ((b[c >> 1] | 0) >>> 1);
            b[z >> 1] = ((b[d + 2 >> 1] | 0) >>> 1) + ((b[A >> 1] | 0) >>> 1);
            b[x >> 1] = ((b[d + 4 >> 1] | 0) >>> 1) + ((b[y >> 1] | 0) >>> 1);
            b[v >> 1] = ((b[d + 6 >> 1] | 0) >>> 1) + ((b[w >> 1] | 0) >>> 1);
            b[t >> 1] = ((b[d + 8 >> 1] | 0) >>> 1) + ((b[u >> 1] | 0) >>> 1);
            b[r >> 1] = ((b[d + 10 >> 1] | 0) >>> 1) + ((b[s >> 1] | 0) >>> 1);
            b[p >> 1] = ((b[d + 12 >> 1] | 0) >>> 1) + ((b[q >> 1] | 0) >>> 1);
            b[n >> 1] = ((b[d + 14 >> 1] | 0) >>> 1) + ((b[o >> 1] | 0) >>> 1);
            b[l >> 1] = ((b[d + 16 >> 1] | 0) >>> 1) + ((b[m >> 1] | 0) >>> 1);
            b[j >> 1] = ((b[d + 18 >> 1] | 0) >>> 1) + ((b[k >> 1] | 0) >>> 1);
            he(h, e + 44 | 0, f);
            he(d, e + 66 | 0, f);
            i = g;
            return
        }

        function $d(a, c, d, e, f) {
            a = a | 0;
            c = c | 0;
            d = d | 0;
            e = e | 0;
            f = f | 0;
            var g = 0, h = 0, j = 0, k = 0, l = 0, m = 0, n = 0, o = 0, p = 0, q = 0, r = 0, s = 0, t = 0, u = 0, v = 0,
                w = 0, x = 0, y = 0, z = 0, A = 0;
            g = i;
            i = i + 32 | 0;
            h = g;
            A = c + 2 | 0;
            z = h + 2 | 0;
            b[h >> 1] = ((b[c >> 1] | 0) >>> 1) + ((b[a >> 1] | 0) >>> 1);
            y = c + 4 | 0;
            x = h + 4 | 0;
            b[z >> 1] = ((b[A >> 1] | 0) >>> 1) + ((b[a + 2 >> 1] | 0) >>> 1);
            w = c + 6 | 0;
            v = h + 6 | 0;
            b[x >> 1] = ((b[y >> 1] | 0) >>> 1) + ((b[a + 4 >> 1] | 0) >>> 1);
            u = c + 8 | 0;
            t = h + 8 | 0;
            b[v >> 1] = ((b[w >> 1] | 0) >>> 1) + ((b[a + 6 >> 1] | 0) >>> 1);
            s = c + 10 | 0;
            r = h + 10 | 0;
            b[t >> 1] = ((b[u >> 1] | 0) >>> 1) + ((b[a + 8 >> 1] | 0) >>> 1);
            q = c + 12 | 0;
            p = h + 12 | 0;
            b[r >> 1] = ((b[s >> 1] | 0) >>> 1) + ((b[a + 10 >> 1] | 0) >>> 1);
            o = c + 14 | 0;
            n = h + 14 | 0;
            b[p >> 1] = ((b[q >> 1] | 0) >>> 1) + ((b[a + 12 >> 1] | 0) >>> 1);
            m = c + 16 | 0;
            l = h + 16 | 0;
            b[n >> 1] = ((b[o >> 1] | 0) >>> 1) + ((b[a + 14 >> 1] | 0) >>> 1);
            k = c + 18 | 0;
            j = h + 18 | 0;
            b[l >> 1] = ((b[m >> 1] | 0) >>> 1) + ((b[a + 16 >> 1] | 0) >>> 1);
            b[j >> 1] = ((b[k >> 1] | 0) >>> 1) + ((b[a + 18 >> 1] | 0) >>> 1);
            he(h, e, f);
            b[h >> 1] = ((b[d >> 1] | 0) >>> 1) + ((b[c >> 1] | 0) >>> 1);
            b[z >> 1] = ((b[d + 2 >> 1] | 0) >>> 1) + ((b[A >> 1] | 0) >>> 1);
            b[x >> 1] = ((b[d + 4 >> 1] | 0) >>> 1) + ((b[y >> 1] | 0) >>> 1);
            b[v >> 1] = ((b[d + 6 >> 1] | 0) >>> 1) + ((b[w >> 1] | 0) >>> 1);
            b[t >> 1] = ((b[d + 8 >> 1] | 0) >>> 1) + ((b[u >> 1] | 0) >>> 1);
            b[r >> 1] = ((b[d + 10 >> 1] | 0) >>> 1) + ((b[s >> 1] | 0) >>> 1);
            b[p >> 1] = ((b[d + 12 >> 1] | 0) >>> 1) + ((b[q >> 1] | 0) >>> 1);
            b[n >> 1] = ((b[d + 14 >> 1] | 0) >>> 1) + ((b[o >> 1] | 0) >>> 1);
            b[l >> 1] = ((b[d + 16 >> 1] | 0) >>> 1) + ((b[m >> 1] | 0) >>> 1);
            b[j >> 1] = ((b[d + 18 >> 1] | 0) >>> 1) + ((b[k >> 1] | 0) >>> 1);
            he(h, e + 44 | 0, f);
            i = g;
            return
        }

        function ae(a, c, d, e) {
            a = a | 0;
            c = c | 0;
            d = d | 0;
            e = e | 0;
            var f = 0, g = 0, h = 0, j = 0, k = 0, l = 0, m = 0, n = 0, o = 0, p = 0, q = 0, r = 0, s = 0, t = 0, u = 0,
                v = 0, w = 0, x = 0, y = 0, z = 0, A = 0, B = 0, C = 0, D = 0, E = 0, F = 0, G = 0, H = 0, I = 0, J = 0;
            f = i;
            i = i + 32 | 0;
            g = f;
            H = b[a >> 1] | 0;
            b[g >> 1] = H - (H >>> 2) + ((b[c >> 1] | 0) >>> 2);
            H = a + 2 | 0;
            E = b[H >> 1] | 0;
            I = c + 2 | 0;
            G = g + 2 | 0;
            b[G >> 1] = E - (E >>> 2) + ((b[I >> 1] | 0) >>> 2);
            E = a + 4 | 0;
            B = b[E >> 1] | 0;
            F = c + 4 | 0;
            D = g + 4 | 0;
            b[D >> 1] = B - (B >>> 2) + ((b[F >> 1] | 0) >>> 2);
            B = a + 6 | 0;
            y = b[B >> 1] | 0;
            C = c + 6 | 0;
            A = g + 6 | 0;
            b[A >> 1] = y - (y >>> 2) + ((b[C >> 1] | 0) >>> 2);
            y = a + 8 | 0;
            v = b[y >> 1] | 0;
            z = c + 8 | 0;
            x = g + 8 | 0;
            b[x >> 1] = v - (v >>> 2) + ((b[z >> 1] | 0) >>> 2);
            v = a + 10 | 0;
            s = b[v >> 1] | 0;
            w = c + 10 | 0;
            u = g + 10 | 0;
            b[u >> 1] = s - (s >>> 2) + ((b[w >> 1] | 0) >>> 2);
            s = a + 12 | 0;
            p = b[s >> 1] | 0;
            t = c + 12 | 0;
            r = g + 12 | 0;
            b[r >> 1] = p - (p >>> 2) + ((b[t >> 1] | 0) >>> 2);
            p = a + 14 | 0;
            m = b[p >> 1] | 0;
            q = c + 14 | 0;
            o = g + 14 | 0;
            b[o >> 1] = m - (m >>> 2) + ((b[q >> 1] | 0) >>> 2);
            m = a + 16 | 0;
            j = b[m >> 1] | 0;
            n = c + 16 | 0;
            l = g + 16 | 0;
            b[l >> 1] = j - (j >>> 2) + ((b[n >> 1] | 0) >>> 2);
            j = a + 18 | 0;
            J = b[j >> 1] | 0;
            k = c + 18 | 0;
            h = g + 18 | 0;
            b[h >> 1] = J - (J >>> 2) + ((b[k >> 1] | 0) >>> 2);
            he(g, d, e);
            b[g >> 1] = ((b[a >> 1] | 0) >>> 1) + ((b[c >> 1] | 0) >>> 1);
            b[G >> 1] = ((b[H >> 1] | 0) >>> 1) + ((b[I >> 1] | 0) >>> 1);
            b[D >> 1] = ((b[E >> 1] | 0) >>> 1) + ((b[F >> 1] | 0) >>> 1);
            b[A >> 1] = ((b[B >> 1] | 0) >>> 1) + ((b[C >> 1] | 0) >>> 1);
            b[x >> 1] = ((b[y >> 1] | 0) >>> 1) + ((b[z >> 1] | 0) >>> 1);
            b[u >> 1] = ((b[v >> 1] | 0) >>> 1) + ((b[w >> 1] | 0) >>> 1);
            b[r >> 1] = ((b[s >> 1] | 0) >>> 1) + ((b[t >> 1] | 0) >>> 1);
            b[o >> 1] = ((b[p >> 1] | 0) >>> 1) + ((b[q >> 1] | 0) >>> 1);
            b[l >> 1] = ((b[m >> 1] | 0) >>> 1) + ((b[n >> 1] | 0) >>> 1);
            b[h >> 1] = ((b[j >> 1] | 0) >>> 1) + ((b[k >> 1] | 0) >>> 1);
            he(g, d + 22 | 0, e);
            J = b[c >> 1] | 0;
            b[g >> 1] = J - (J >>> 2) + ((b[a >> 1] | 0) >>> 2);
            a = b[I >> 1] | 0;
            b[G >> 1] = a - (a >>> 2) + ((b[H >> 1] | 0) >>> 2);
            a = b[F >> 1] | 0;
            b[D >> 1] = a - (a >>> 2) + ((b[E >> 1] | 0) >>> 2);
            a = b[C >> 1] | 0;
            b[A >> 1] = a - (a >>> 2) + ((b[B >> 1] | 0) >>> 2);
            a = b[z >> 1] | 0;
            b[x >> 1] = a - (a >>> 2) + ((b[y >> 1] | 0) >>> 2);
            a = b[w >> 1] | 0;
            b[u >> 1] = a - (a >>> 2) + ((b[v >> 1] | 0) >>> 2);
            a = b[t >> 1] | 0;
            b[r >> 1] = a - (a >>> 2) + ((b[s >> 1] | 0) >>> 2);
            a = b[q >> 1] | 0;
            b[o >> 1] = a - (a >>> 2) + ((b[p >> 1] | 0) >>> 2);
            a = b[n >> 1] | 0;
            b[l >> 1] = a - (a >>> 2) + ((b[m >> 1] | 0) >>> 2);
            a = b[k >> 1] | 0;
            b[h >> 1] = a - (a >>> 2) + ((b[j >> 1] | 0) >>> 2);
            he(g, d + 44 | 0, e);
            he(c, d + 66 | 0, e);
            i = f;
            return
        }

        function be(a, c, d, e) {
            a = a | 0;
            c = c | 0;
            d = d | 0;
            e = e | 0;
            var f = 0, g = 0, h = 0, j = 0, k = 0, l = 0, m = 0, n = 0, o = 0, p = 0, q = 0, r = 0, s = 0, t = 0, u = 0,
                v = 0, w = 0, x = 0, y = 0, z = 0, A = 0, B = 0, C = 0, D = 0, E = 0, F = 0, G = 0, H = 0, I = 0, J = 0;
            f = i;
            i = i + 32 | 0;
            g = f;
            H = b[a >> 1] | 0;
            b[g >> 1] = H - (H >>> 2) + ((b[c >> 1] | 0) >>> 2);
            H = a + 2 | 0;
            E = b[H >> 1] | 0;
            I = c + 2 | 0;
            G = g + 2 | 0;
            b[G >> 1] = E - (E >>> 2) + ((b[I >> 1] | 0) >>> 2);
            E = a + 4 | 0;
            B = b[E >> 1] | 0;
            F = c + 4 | 0;
            D = g + 4 | 0;
            b[D >> 1] = B - (B >>> 2) + ((b[F >> 1] | 0) >>> 2);
            B = a + 6 | 0;
            y = b[B >> 1] | 0;
            C = c + 6 | 0;
            A = g + 6 | 0;
            b[A >> 1] = y - (y >>> 2) + ((b[C >> 1] | 0) >>> 2);
            y = a + 8 | 0;
            v = b[y >> 1] | 0;
            z = c + 8 | 0;
            x = g + 8 | 0;
            b[x >> 1] = v - (v >>> 2) + ((b[z >> 1] | 0) >>> 2);
            v = a + 10 | 0;
            s = b[v >> 1] | 0;
            w = c + 10 | 0;
            u = g + 10 | 0;
            b[u >> 1] = s - (s >>> 2) + ((b[w >> 1] | 0) >>> 2);
            s = a + 12 | 0;
            p = b[s >> 1] | 0;
            t = c + 12 | 0;
            r = g + 12 | 0;
            b[r >> 1] = p - (p >>> 2) + ((b[t >> 1] | 0) >>> 2);
            p = a + 14 | 0;
            m = b[p >> 1] | 0;
            q = c + 14 | 0;
            o = g + 14 | 0;
            b[o >> 1] = m - (m >>> 2) + ((b[q >> 1] | 0) >>> 2);
            m = a + 16 | 0;
            j = b[m >> 1] | 0;
            n = c + 16 | 0;
            l = g + 16 | 0;
            b[l >> 1] = j - (j >>> 2) + ((b[n >> 1] | 0) >>> 2);
            j = a + 18 | 0;
            J = b[j >> 1] | 0;
            k = c + 18 | 0;
            h = g + 18 | 0;
            b[h >> 1] = J - (J >>> 2) + ((b[k >> 1] | 0) >>> 2);
            he(g, d, e);
            b[g >> 1] = ((b[a >> 1] | 0) >>> 1) + ((b[c >> 1] | 0) >>> 1);
            b[G >> 1] = ((b[H >> 1] | 0) >>> 1) + ((b[I >> 1] | 0) >>> 1);
            b[D >> 1] = ((b[E >> 1] | 0) >>> 1) + ((b[F >> 1] | 0) >>> 1);
            b[A >> 1] = ((b[B >> 1] | 0) >>> 1) + ((b[C >> 1] | 0) >>> 1);
            b[x >> 1] = ((b[y >> 1] | 0) >>> 1) + ((b[z >> 1] | 0) >>> 1);
            b[u >> 1] = ((b[v >> 1] | 0) >>> 1) + ((b[w >> 1] | 0) >>> 1);
            b[r >> 1] = ((b[s >> 1] | 0) >>> 1) + ((b[t >> 1] | 0) >>> 1);
            b[o >> 1] = ((b[p >> 1] | 0) >>> 1) + ((b[q >> 1] | 0) >>> 1);
            b[l >> 1] = ((b[m >> 1] | 0) >>> 1) + ((b[n >> 1] | 0) >>> 1);
            b[h >> 1] = ((b[j >> 1] | 0) >>> 1) + ((b[k >> 1] | 0) >>> 1);
            he(g, d + 22 | 0, e);
            c = b[c >> 1] | 0;
            b[g >> 1] = c - (c >>> 2) + ((b[a >> 1] | 0) >>> 2);
            a = b[I >> 1] | 0;
            b[G >> 1] = a - (a >>> 2) + ((b[H >> 1] | 0) >>> 2);
            a = b[F >> 1] | 0;
            b[D >> 1] = a - (a >>> 2) + ((b[E >> 1] | 0) >>> 2);
            a = b[C >> 1] | 0;
            b[A >> 1] = a - (a >>> 2) + ((b[B >> 1] | 0) >>> 2);
            a = b[z >> 1] | 0;
            b[x >> 1] = a - (a >>> 2) + ((b[y >> 1] | 0) >>> 2);
            a = b[w >> 1] | 0;
            b[u >> 1] = a - (a >>> 2) + ((b[v >> 1] | 0) >>> 2);
            a = b[t >> 1] | 0;
            b[r >> 1] = a - (a >>> 2) + ((b[s >> 1] | 0) >>> 2);
            a = b[q >> 1] | 0;
            b[o >> 1] = a - (a >>> 2) + ((b[p >> 1] | 0) >>> 2);
            a = b[n >> 1] | 0;
            b[l >> 1] = a - (a >>> 2) + ((b[m >> 1] | 0) >>> 2);
            a = b[k >> 1] | 0;
            b[h >> 1] = a - (a >>> 2) + ((b[j >> 1] | 0) >>> 2);
            he(g, d + 44 | 0, e);
            i = f;
            return
        }

        function ce(a, c) {
            a = a | 0;
            c = c | 0;
            var d = 0, f = 0;
            if ((a | 0) < 1) {
                c = 1073741823;
                return c | 0
            }
            d = (pe(a) | 0) << 16 >> 16;
            c = 30 - d | 0;
            a = a << d >> (c & 1 ^ 1);
            d = (a >> 25 << 16) + -1048576 >> 16;
            f = b[7030 + (d << 1) >> 1] | 0;
            c = (f << 16) - (Z(f - (e[7030 + (d + 1 << 1) >> 1] | 0) << 16 >> 15, a >>> 10 & 32767) | 0) >> (c << 16 >> 17) + 1;
            return c | 0
        }

        function de(a, b, c, d) {
            a = a | 0;
            b = b | 0;
            c = c | 0;
            d = d | 0;
            d = pe(a) | 0;
            ee(a << (d << 16 >> 16), d, b, c);
            return
        }

        function ee(a, c, d, f) {
            a = a | 0;
            c = c | 0;
            d = d | 0;
            f = f | 0;
            if ((a | 0) < 1) {
                b[d >> 1] = 0;
                d = 0;
                b[f >> 1] = d;
                return
            } else {
                b[d >> 1] = 30 - (c & 65535);
                d = (a >> 25 << 16) + -2097152 >> 16;
                c = b[7128 + (d << 1) >> 1] | 0;
                d = ((c << 16) - (Z(a >>> 9 & 65534, c - (e[7128 + (d + 1 << 1) >> 1] | 0) << 16 >> 16) | 0) | 0) >>> 16 & 65535;
                b[f >> 1] = d;
                return
            }
        }

        function fe(a, c, d) {
            a = a | 0;
            c = c | 0;
            d = d | 0;
            var f = 0, g = 0;
            f = a + 2 | 0;
            d = b[f >> 1] | 0;
            b[c >> 1] = d;
            g = a + 4 | 0;
            b[c + 2 >> 1] = (e[g >> 1] | 0) - (e[a >> 1] | 0);
            b[c + 4 >> 1] = (e[a + 6 >> 1] | 0) - (e[f >> 1] | 0);
            f = a + 8 | 0;
            b[c + 6 >> 1] = (e[f >> 1] | 0) - (e[g >> 1] | 0);
            b[c + 8 >> 1] = (e[a + 10 >> 1] | 0) - (e[a + 6 >> 1] | 0);
            g = a + 12 | 0;
            b[c + 10 >> 1] = (e[g >> 1] | 0) - (e[f >> 1] | 0);
            b[c + 12 >> 1] = (e[a + 14 >> 1] | 0) - (e[a + 10 >> 1] | 0);
            b[c + 14 >> 1] = (e[a + 16 >> 1] | 0) - (e[g >> 1] | 0);
            b[c + 16 >> 1] = (e[a + 18 >> 1] | 0) - (e[a + 14 >> 1] | 0);
            b[c + 18 >> 1] = 16384 - (e[a + 16 >> 1] | 0);
            a = 10;
            g = c;
            while (1) {
                d = d << 16 >> 16;
                c = (d << 16) + -120782848 | 0;
                if ((c | 0) > 0) c = 1843 - ((c >> 16) * 12484 >> 16) | 0; else c = 3427 - ((d * 56320 | 0) >>> 16) | 0;
                f = g + 2 | 0;
                b[g >> 1] = c << 3;
                a = a + -1 << 16 >> 16;
                if (!(a << 16 >> 16)) break;
                d = b[f >> 1] | 0;
                g = f
            }
            return
        }

        function ge(a, b, c) {
            a = a | 0;
            b = b | 0;
            c = c | 0;
            c = b << 16 >> 16;
            if (b << 16 >> 16 > 31) {
                b = 0;
                return b | 0
            }
            if (b << 16 >> 16 > 0) return ((1 << c + -1 & a | 0) != 0 & 1) + (b << 16 >> 16 < 31 ? a >> c : 0) | 0;
            c = 0 - c << 16 >> 16;
            b = a << c;
            b = (b >> c | 0) == (a | 0) ? b : a >> 31 ^ 2147483647;
            return b | 0
        }

        function he(a, d, e) {
            a = a | 0;
            d = d | 0;
            e = e | 0;
            var f = 0, g = 0, h = 0, j = 0, k = 0, l = 0, m = 0, n = 0, o = 0, p = 0, q = 0, r = 0, s = 0, t = 0;
            s = i;
            i = i + 48 | 0;
            q = s + 24 | 0;
            r = s;
            o = q + 4 | 0;
            c[q >> 2] = 16777216;
            f = 0 - (b[a >> 1] | 0) | 0;
            p = q + 8 | 0;
            c[o >> 2] = f << 10;
            g = b[a + 4 >> 1] | 0;
            l = f >> 6;
            c[p >> 2] = 33554432 - (((Z((f << 9) - (l << 15) << 16 >> 16, g) | 0) >> 15) + (Z(l, g) | 0) << 2);
            l = q + 4 | 0;
            g = (c[l >> 2] | 0) - (g << 10) | 0;
            c[l >> 2] = g;
            l = q + 12 | 0;
            f = q + 4 | 0;
            c[l >> 2] = g;
            e = b[a + 8 >> 1] | 0;
            h = g;
            m = 1;
            while (1) {
                k = l + -4 | 0;
                j = c[k >> 2] | 0;
                n = j >> 16;
                c[l >> 2] = h + g - (((Z((j >>> 1) - (n << 15) << 16 >> 16, e) | 0) >> 15) + (Z(n, e) | 0) << 2);
                if ((m | 0) == 2) break;
                h = c[l + -12 >> 2] | 0;
                l = k;
                g = j;
                m = m + 1 | 0
            }
            c[f >> 2] = (c[f >> 2] | 0) - (e << 10);
            e = q + 16 | 0;
            f = c[q + 8 >> 2] | 0;
            c[e >> 2] = f;
            k = b[a + 12 >> 1] | 0;
            g = f;
            l = 1;
            while (1) {
                j = e + -4 | 0;
                h = c[j >> 2] | 0;
                n = h >> 16;
                c[e >> 2] = g + f - (((Z((h >>> 1) - (n << 15) << 16 >> 16, k) | 0) >> 15) + (Z(n, k) | 0) << 2);
                if ((l | 0) == 3) break;
                g = c[e + -12 >> 2] | 0;
                e = j;
                f = h;
                l = l + 1 | 0
            }
            e = q + 4 | 0;
            c[e >> 2] = (c[e >> 2] | 0) - (k << 10);
            e = q + 20 | 0;
            g = c[q + 12 >> 2] | 0;
            c[e >> 2] = g;
            f = b[a + 16 >> 1] | 0;
            h = g;
            l = 1;
            while (1) {
                k = e + -4 | 0;
                j = c[k >> 2] | 0;
                n = j >> 16;
                c[e >> 2] = h + g - (((Z((j >>> 1) - (n << 15) << 16 >> 16, f) | 0) >> 15) + (Z(n, f) | 0) << 2);
                if ((l | 0) == 4) break;
                h = c[e + -12 >> 2] | 0;
                e = k;
                g = j;
                l = l + 1 | 0
            }
            l = q + 4 | 0;
            c[l >> 2] = (c[l >> 2] | 0) - (f << 10);
            c[r >> 2] = 16777216;
            l = 0 - (b[a + 2 >> 1] | 0) | 0;
            n = r + 8 | 0;
            c[r + 4 >> 2] = l << 10;
            f = b[a + 6 >> 1] | 0;
            m = l >> 6;
            c[n >> 2] = 33554432 - (((Z((l << 9) - (m << 15) << 16 >> 16, f) | 0) >> 15) + (Z(m, f) | 0) << 2);
            m = r + 4 | 0;
            f = (c[m >> 2] | 0) - (f << 10) | 0;
            c[m >> 2] = f;
            m = r + 12 | 0;
            l = r + 4 | 0;
            c[m >> 2] = f;
            k = b[a + 10 >> 1] | 0;
            g = f;
            e = 1;
            while (1) {
                j = m + -4 | 0;
                h = c[j >> 2] | 0;
                t = h >> 16;
                c[m >> 2] = g + f - (((Z((h >>> 1) - (t << 15) << 16 >> 16, k) | 0) >> 15) + (Z(t, k) | 0) << 2);
                if ((e | 0) == 2) break;
                g = c[m + -12 >> 2] | 0;
                m = j;
                f = h;
                e = e + 1 | 0
            }
            c[l >> 2] = (c[l >> 2] | 0) - (k << 10);
            l = r + 16 | 0;
            f = c[r + 8 >> 2] | 0;
            c[l >> 2] = f;
            k = b[a + 14 >> 1] | 0;
            g = f;
            e = 1;
            while (1) {
                j = l + -4 | 0;
                h = c[j >> 2] | 0;
                t = h >> 16;
                c[l >> 2] = g + f - (((Z((h >>> 1) - (t << 15) << 16 >> 16, k) | 0) >> 15) + (Z(t, k) | 0) << 2);
                if ((e | 0) == 3) break;
                g = c[l + -12 >> 2] | 0;
                l = j;
                f = h;
                e = e + 1 | 0
            }
            e = r + 4 | 0;
            c[e >> 2] = (c[e >> 2] | 0) - (k << 10);
            e = r + 20 | 0;
            k = c[r + 12 >> 2] | 0;
            c[e >> 2] = k;
            f = b[a + 18 >> 1] | 0;
            j = k;
            l = 1;
            while (1) {
                g = e + -4 | 0;
                h = c[g >> 2] | 0;
                t = h >> 16;
                c[e >> 2] = j + k - (((Z((h >>> 1) - (t << 15) << 16 >> 16, f) | 0) >> 15) + (Z(t, f) | 0) << 2);
                if ((l | 0) == 4) break;
                j = c[e + -12 >> 2] | 0;
                e = g;
                k = h;
                l = l + 1 | 0
            }
            j = (c[r + 4 >> 2] | 0) - (f << 10) | 0;
            m = q + 20 | 0;
            k = r + 20 | 0;
            l = c[q + 16 >> 2] | 0;
            a = (c[m >> 2] | 0) + l | 0;
            c[m >> 2] = a;
            m = c[r + 16 >> 2] | 0;
            t = (c[k >> 2] | 0) - m | 0;
            c[k >> 2] = t;
            k = c[q + 12 >> 2] | 0;
            l = l + k | 0;
            c[q + 16 >> 2] = l;
            h = c[r + 12 >> 2] | 0;
            m = m - h | 0;
            c[r + 16 >> 2] = m;
            f = c[p >> 2] | 0;
            k = k + f | 0;
            c[q + 12 >> 2] = k;
            g = c[n >> 2] | 0;
            p = h - g | 0;
            c[r + 12 >> 2] = p;
            h = c[o >> 2] | 0;
            n = f + h | 0;
            c[q + 8 >> 2] = n;
            o = g - j | 0;
            c[r + 8 >> 2] = o;
            q = h + (c[q >> 2] | 0) | 0;
            r = j - (c[r >> 2] | 0) | 0;
            b[d >> 1] = 4096;
            q = q + 4096 | 0;
            b[d + 2 >> 1] = (q + r | 0) >>> 13;
            b[d + 20 >> 1] = (q - r | 0) >>> 13;
            r = n + 4096 | 0;
            b[d + 4 >> 1] = (r + o | 0) >>> 13;
            b[d + 18 >> 1] = (r - o | 0) >>> 13;
            r = k + 4096 | 0;
            b[d + 6 >> 1] = (r + p | 0) >>> 13;
            b[d + 16 >> 1] = (r - p | 0) >>> 13;
            r = l + 4096 | 0;
            b[d + 8 >> 1] = (r + m | 0) >>> 13;
            b[d + 14 >> 1] = (r - m | 0) >>> 13;
            r = a + 4096 | 0;
            b[d + 10 >> 1] = (r + t | 0) >>> 13;
            b[d + 12 >> 1] = (r - t | 0) >>> 13;
            i = s;
            return
        }

        function ie(a) {
            a = a | 0;
            var d = 0, e = 0, f = 0, g = 0, h = 0;
            if (!a) {
                h = -1;
                return h | 0
            }
            c[a >> 2] = 0;
            d = Je(44) | 0;
            if (!d) {
                h = -1;
                return h | 0
            }
            e = d + 40 | 0;
            if ((xe(e) | 0) << 16 >> 16) {
                h = -1;
                return h | 0
            }
            f = d;
            g = 7452;
            h = f + 20 | 0;
            do {
                b[f >> 1] = b[g >> 1] | 0;
                f = f + 2 | 0;
                g = g + 2 | 0
            } while ((f | 0) < (h | 0));
            f = d + 20 | 0;
            g = 7452;
            h = f + 20 | 0;
            do {
                b[f >> 1] = b[g >> 1] | 0;
                f = f + 2 | 0;
                g = g + 2 | 0
            } while ((f | 0) < (h | 0));
            ye(c[e >> 2] | 0) | 0;
            c[a >> 2] = d;
            h = 0;
            return h | 0
        }

        function je(a) {
            a = a | 0;
            var d = 0, e = 0, f = 0;
            if (!a) {
                f = -1;
                return f | 0
            }
            d = a;
            e = 7452;
            f = d + 20 | 0;
            do {
                b[d >> 1] = b[e >> 1] | 0;
                d = d + 2 | 0;
                e = e + 2 | 0
            } while ((d | 0) < (f | 0));
            d = a + 20 | 0;
            e = 7452;
            f = d + 20 | 0;
            do {
                b[d >> 1] = b[e >> 1] | 0;
                d = d + 2 | 0;
                e = e + 2 | 0
            } while ((d | 0) < (f | 0));
            ye(c[a + 40 >> 2] | 0) | 0;
            f = 0;
            return f | 0
        }

        function ke(a) {
            a = a | 0;
            var b = 0;
            if (!a) return;
            b = c[a >> 2] | 0;
            if (!b) return;
            ze(b + 40 | 0);
            Ke(c[a >> 2] | 0);
            c[a >> 2] = 0;
            return
        }

        function le(a, d, e, f, g, h, j, k) {
            a = a | 0;
            d = d | 0;
            e = e | 0;
            f = f | 0;
            g = g | 0;
            h = h | 0;
            j = j | 0;
            k = k | 0;
            var l = 0, m = 0, n = 0, o = 0, p = 0;
            p = i;
            i = i + 64 | 0;
            o = p + 44 | 0;
            l = p + 24 | 0;
            m = p + 4 | 0;
            n = p;
            if ((d | 0) == 7) {
                Sd(f + 22 | 0, l, a, k);
                Sd(f + 66 | 0, h, l, k);
                $d(a, l, h, f, k);
                if ((e | 0) == 8) f = 6; else {
                    ve(c[a + 40 >> 2] | 0, l, h, m, o, c[j >> 2] | 0, k);
                    _d(a + 20 | 0, m, o, g, k);
                    g = (c[j >> 2] | 0) + 10 | 0;
                    f = 7
                }
            } else {
                Sd(f + 66 | 0, h, a, k);
                be(a, h, f, k);
                if ((e | 0) == 8) f = 6; else {
                    te(c[a + 40 >> 2] | 0, d, h, o, c[j >> 2] | 0, n, k);
                    ae(a + 20 | 0, o, g, k);
                    g = (c[j >> 2] | 0) + 6 | 0;
                    f = 7
                }
            }
            if ((f | 0) == 6) {
                _abort();//fix cc 精简
            } else if ((f | 0) == 7) {
                c[j >> 2] = g;
                f = a;
                g = f + 20 | 0;
                do {
                    b[f >> 1] = b[h >> 1] | 0;
                    f = f + 2 | 0;
                    h = h + 2 | 0
                } while ((f | 0) < (g | 0));
                f = a + 20 | 0;
                h = o;
                g = f + 20 | 0;
                do {
                    b[f >> 1] = b[h >> 1] | 0;
                    f = f + 2 | 0;
                    h = h + 2 | 0
                } while ((f | 0) < (g | 0));
                i = p;
                return
            }
        }

        function me(a, c, d, e) {
            a = a | 0;
            c = c | 0;
            d = d | 0;
            e = e | 0;
            var f = 0, g = 0, h = 0;
            if (d << 16 >> 16 > 0) e = 0; else return;
            do {
                g = b[a + (e << 1) >> 1] | 0;
                h = g >> 8;
                f = b[7194 + (h << 1) >> 1] | 0;
                b[c + (e << 1) >> 1] = ((Z((b[7194 + (h + 1 << 1) >> 1] | 0) - f | 0, g & 255) | 0) >>> 8) + f;
                e = e + 1 | 0
            } while ((e & 65535) << 16 >> 16 != d << 16 >> 16);
            return
        }

        function ne(a, c, d, e) {
            a = a | 0;
            c = c | 0;
            d = d | 0;
            e = e | 0;
            var f = 0, g = 0, h = 0;
            e = (d << 16 >> 16) + -1 | 0;
            d = e & 65535;
            if (d << 16 >> 16 <= -1) return;
            f = 63;
            h = c + (e << 1) | 0;
            g = a + (e << 1) | 0;
            while (1) {
                a = b[g >> 1] | 0;
                c = f;
                while (1) {
                    e = c << 16 >> 16;
                    f = b[7194 + (e << 1) >> 1] | 0;
                    if (a << 16 >> 16 > f << 16 >> 16) c = c + -1 << 16 >> 16; else break
                }
                b[h >> 1] = (((Z(b[7324 + (e << 1) >> 1] | 0, (a << 16 >> 16) - (f << 16 >> 16) | 0) | 0) + 2048 | 0) >>> 12) + (e << 8);
                d = d + -1 << 16 >> 16;
                if (d << 16 >> 16 > -1) {
                    f = c;
                    h = h + -2 | 0;
                    g = g + -2 | 0
                } else break
            }
            return
        }

        //fix cc 精简

        function pe(a) {
            a = a | 0;
            var b = 0;
            a:do if ((a | 0) != 0 ? (b = a - (a >>> 31) | 0, b = b >> 31 ^ b, (b & 1073741824 | 0) == 0) : 0) {
                a = b;
                b = 0;
                while (1) {
                    if (a & 536870912) {
                        a = 7;
                        break
                    }
                    if (a & 268435456) {
                        a = 8;
                        break
                    }
                    if (a & 134217728) {
                        a = 9;
                        break
                    }
                    b = b + 4 << 16 >> 16;
                    a = a << 4;
                    if (a & 1073741824) break a
                }
                if ((a | 0) == 7) {
                    b = b | 1;
                    break
                } else if ((a | 0) == 8) {
                    b = b | 2;
                    break
                } else if ((a | 0) == 9) {
                    b = b | 3;
                    break
                }
            } else b = 0; while (0);
            return b | 0
        }

        function qe(a) {
            a = a | 0;
            var b = 0, c = 0;
            if (!(a << 16 >> 16)) {
                c = 0;
                return c | 0
            }
            b = (a & 65535) - ((a & 65535) >>> 15 & 65535) | 0;
            b = (b << 16 >> 31 ^ b) << 16;
            a = b >> 16;
            if (!(a & 16384)) {
                c = b;
                b = 0
            } else {
                c = 0;
                return c | 0
            }
            while (1) {
                if (a & 8192) {
                    a = b;
                    c = 7;
                    break
                }
                if (a & 4096) {
                    a = b;
                    c = 8;
                    break
                }
                if (a & 2048) {
                    a = b;
                    c = 9;
                    break
                }
                b = b + 4 << 16 >> 16;
                c = c << 4;
                a = c >> 16;
                if (a & 16384) {
                    a = b;
                    c = 10;
                    break
                }
            }
            if ((c | 0) == 7) {
                c = a | 1;
                return c | 0
            } else if ((c | 0) == 8) {
                c = a | 2;
                return c | 0
            } else if ((c | 0) == 9) {
                c = a | 3;
                return c | 0
            } else if ((c | 0) == 10) return a | 0;
            return 0
        }

        function re(a, d, f) {
            a = a | 0;
            d = d | 0;
            f = f | 0;
            var g = 0, h = 0, i = 0;
            d = d << 16 >> 16;
            if ((d & 134217727 | 0) == 33554432) {
                c[f >> 2] = 1;
                d = 2147483647
            } else d = d << 6;
            g = d >>> 16 & 31;
            i = b[7792 + (g << 1) >> 1] | 0;
            h = i << 16;
            d = Z(i - (e[7792 + (g + 1 << 1) >> 1] | 0) << 16 >> 16, d >>> 1 & 32767) | 0;
            if ((d | 0) == 1073741824) {
                c[f >> 2] = 1;
                g = 2147483647
            } else g = d << 1;
            d = h - g | 0;
            if (((d ^ h) & (g ^ h) | 0) >= 0) {
                i = d;
                a = a & 65535;
                a = 30 - a | 0;
                a = a & 65535;
                f = ge(i, a, f) | 0;
                return f | 0
            }
            c[f >> 2] = 1;
            i = (i >>> 15 & 1) + 2147483647 | 0;
            a = a & 65535;
            a = 30 - a | 0;
            a = a & 65535;
            f = ge(i, a, f) | 0;
            return f | 0
        }

        function se(a, c, d, e, f, g) {
            a = a | 0;
            c = c | 0;
            d = d | 0;
            e = e | 0;
            f = f | 0;
            g = g | 0;
            var h = 0, j = 0, k = 0, l = 0, m = 0, n = 0, o = 0, p = 0, q = 0, r = 0, s = 0;
            o = i;
            i = i + 48 | 0;
            n = o;
            m = 0 - (d & 65535) | 0;
            m = f << 16 >> 16 == 0 ? m : m << 1 & 131070;
            d = m & 65535;
            m = (d << 16 >> 16 < 0 ? m + 6 | 0 : m) << 16 >> 16;
            g = 6 - m | 0;
            b[n >> 1] = b[7858 + (m << 1) >> 1] | 0;
            b[n + 2 >> 1] = b[7858 + (g << 1) >> 1] | 0;
            b[n + 4 >> 1] = b[7858 + (m + 6 << 1) >> 1] | 0;
            b[n + 6 >> 1] = b[7858 + (g + 6 << 1) >> 1] | 0;
            b[n + 8 >> 1] = b[7858 + (m + 12 << 1) >> 1] | 0;
            b[n + 10 >> 1] = b[7858 + (g + 12 << 1) >> 1] | 0;
            b[n + 12 >> 1] = b[7858 + (m + 18 << 1) >> 1] | 0;
            b[n + 14 >> 1] = b[7858 + (g + 18 << 1) >> 1] | 0;
            b[n + 16 >> 1] = b[7858 + (m + 24 << 1) >> 1] | 0;
            b[n + 18 >> 1] = b[7858 + (g + 24 << 1) >> 1] | 0;
            b[n + 20 >> 1] = b[7858 + (m + 30 << 1) >> 1] | 0;
            b[n + 22 >> 1] = b[7858 + (g + 30 << 1) >> 1] | 0;
            b[n + 24 >> 1] = b[7858 + (m + 36 << 1) >> 1] | 0;
            b[n + 26 >> 1] = b[7858 + (g + 36 << 1) >> 1] | 0;
            b[n + 28 >> 1] = b[7858 + (m + 42 << 1) >> 1] | 0;
            b[n + 30 >> 1] = b[7858 + (g + 42 << 1) >> 1] | 0;
            b[n + 32 >> 1] = b[7858 + (m + 48 << 1) >> 1] | 0;
            b[n + 34 >> 1] = b[7858 + (g + 48 << 1) >> 1] | 0;
            b[n + 36 >> 1] = b[7858 + (m + 54 << 1) >> 1] | 0;
            b[n + 38 >> 1] = b[7858 + (g + 54 << 1) >> 1] | 0;
            g = e << 16 >> 16 >>> 1 & 65535;
            if (!(g << 16 >> 16)) {
                i = o;
                return
            }
            m = a + ((d << 16 >> 16 >> 15 << 16 >> 16) - (c << 16 >> 16) << 1) | 0;
            while (1) {
                l = m + 2 | 0;
                h = b[l >> 1] | 0;
                c = h;
                e = m;
                j = 5;
                k = n;
                f = 16384;
                d = 16384;
                while (1) {
                    q = b[k >> 1] | 0;
                    r = (Z(q, c << 16 >> 16) | 0) + d | 0;
                    p = b[l + -2 >> 1] | 0;
                    d = (Z(p, q) | 0) + f | 0;
                    q = e;
                    e = e + 4 | 0;
                    s = b[k + 2 >> 1] | 0;
                    d = d + (Z(s, h << 16 >> 16) | 0) | 0;
                    f = b[e >> 1] | 0;
                    s = r + (Z(f, s) | 0) | 0;
                    l = l + -4 | 0;
                    r = b[k + 4 >> 1] | 0;
                    p = s + (Z(r, p) | 0) | 0;
                    c = b[l >> 1] | 0;
                    r = d + (Z(c << 16 >> 16, r) | 0) | 0;
                    d = b[k + 6 >> 1] | 0;
                    f = r + (Z(d, f) | 0) | 0;
                    h = b[q + 6 >> 1] | 0;
                    d = p + (Z(h << 16 >> 16, d) | 0) | 0;
                    if (j << 16 >> 16 <= 1) break; else {
                        j = j + -1 << 16 >> 16;
                        k = k + 8 | 0
                    }
                }
                b[a >> 1] = f >>> 15;
                b[a + 2 >> 1] = d >>> 15;
                g = g + -1 << 16 >> 16;
                if (!(g << 16 >> 16)) break; else {
                    m = m + 4 | 0;
                    a = a + 4 | 0
                }
            }
            i = o;
            return
        }

        function te(a, c, d, f, g, h, j) {
            a = a | 0;
            c = c | 0;
            d = d | 0;
            f = f | 0;
            g = g | 0;
            h = h | 0;
            j = j | 0;
            var k = 0, l = 0, m = 0, n = 0, o = 0, p = 0, q = 0, r = 0, s = 0, t = 0, u = 0, v = 0, w = 0, x = 0, y = 0,
                z = 0, A = 0, B = 0, C = 0;
            C = i;
            i = i + 144 | 0;
            t = C + 120 | 0;
            y = C + 100 | 0;
            A = C + 80 | 0;
            B = C + 60 | 0;
            z = C + 40 | 0;
            q = C + 20 | 0;
            r = C;
            ne(d, t, 10, j);
            fe(t, y, j);
            if ((c | 0) == 8) {
                _abort();//fix cc 精简
            } else {
                d = 0;
                do {
                    x = Z(b[8160 + (d << 1) >> 1] | 0, b[a + (d << 1) >> 1] | 0) | 0;
                    x = (x >>> 15) + (e[8140 + (d << 1) >> 1] | 0) | 0;
                    b[A + (d << 1) >> 1] = x;
                    b[B + (d << 1) >> 1] = (e[t + (d << 1) >> 1] | 0) - x;
                    d = d + 1 | 0
                } while ((d | 0) != 10)
            }
            do if (c >>> 0 >= 2) {
                x = B + 2 | 0;
                w = B + 4 | 0;
                v = e[B >> 1] | 0;
                u = b[y >> 1] << 1;
                t = e[x >> 1] | 0;
                q = b[y + 2 >> 1] << 1;
                p = e[w >> 1] | 0;
                o = b[y + 4 >> 1] << 1;
                if ((c | 0) == 5) {
                    r = 2147483647;
                    h = 0;
                    d = 0;
                    s = 17908;
                    while (1) {
                        m = (Z(v - (e[s >> 1] | 0) << 16 >> 16, u) | 0) >> 16;
                        m = Z(m, m) | 0;
                        n = (Z(t - (e[s + 2 >> 1] | 0) << 16 >> 16, q) | 0) >> 16;
                        m = (Z(n, n) | 0) + m | 0;
                        n = (Z(p - (e[s + 4 >> 1] | 0) << 16 >> 16, o) | 0) >> 16;
                        n = m + (Z(n, n) | 0) | 0;
                        m = (n | 0) < (r | 0);
                        d = m ? h : d;
                        h = h + 1 << 16 >> 16;
                        if (h << 16 >> 16 >= 512) break; else {
                            r = m ? n : r;
                            s = s + 6 | 0
                        }
                    }
                    n = (d << 16 >> 16) * 3 | 0;
                    b[B >> 1] = b[17908 + (n << 1) >> 1] | 0;
                    b[x >> 1] = b[17908 + (n + 1 << 1) >> 1] | 0;
                    b[w >> 1] = b[17908 + (n + 2 << 1) >> 1] | 0;
                    b[g >> 1] = d;
                    n = B + 6 | 0;
                    m = B + 8 | 0;
                    v = B + 10 | 0;
                    s = e[n >> 1] | 0;
                    h = b[y + 6 >> 1] << 1;
                    r = e[m >> 1] | 0;
                    q = b[y + 8 >> 1] << 1;
                    p = e[v >> 1] | 0;
                    o = b[y + 10 >> 1] << 1;
                    k = 2147483647;
                    t = 0;
                    d = 0;
                    u = 9716;
                    while (1) {
                        l = (Z(h, s - (e[u >> 1] | 0) << 16 >> 16) | 0) >> 16;
                        l = Z(l, l) | 0;
                        c = (Z(q, r - (e[u + 2 >> 1] | 0) << 16 >> 16) | 0) >> 16;
                        l = (Z(c, c) | 0) + l | 0;
                        c = (Z(o, p - (e[u + 4 >> 1] | 0) << 16 >> 16) | 0) >> 16;
                        c = l + (Z(c, c) | 0) | 0;
                        l = (c | 0) < (k | 0);
                        d = l ? t : d;
                        t = t + 1 << 16 >> 16;
                        if (t << 16 >> 16 >= 512) break; else {
                            k = l ? c : k;
                            u = u + 6 | 0
                        }
                    }
                    k = (d << 16 >> 16) * 3 | 0;
                    b[n >> 1] = b[9716 + (k << 1) >> 1] | 0;
                    b[m >> 1] = b[9716 + (k + 1 << 1) >> 1] | 0;
                    b[v >> 1] = b[9716 + (k + 2 << 1) >> 1] | 0;
                    b[g + 2 >> 1] = d;
                    k = B + 12 | 0;
                    b[g + 4 >> 1] = ue(k, 12788, y + 12 | 0, 512) | 0;
                    t = x;
                    s = w;
                    d = v;
                    l = B;
                    break
                } else {
                    r = 2147483647;
                    h = 0;
                    d = 0;
                    s = 8180;
                    while (1) {
                        m = (Z(v - (e[s >> 1] | 0) << 16 >> 16, u) | 0) >> 16;
                        m = Z(m, m) | 0;
                        n = (Z(t - (e[s + 2 >> 1] | 0) << 16 >> 16, q) | 0) >> 16;
                        m = (Z(n, n) | 0) + m | 0;
                        n = (Z(p - (e[s + 4 >> 1] | 0) << 16 >> 16, o) | 0) >> 16;
                        n = m + (Z(n, n) | 0) | 0;
                        m = (n | 0) < (r | 0);
                        d = m ? h : d;
                        h = h + 1 << 16 >> 16;
                        if (h << 16 >> 16 >= 256) break; else {
                            r = m ? n : r;
                            s = s + 6 | 0
                        }
                    }
                    n = (d << 16 >> 16) * 3 | 0;
                    b[B >> 1] = b[8180 + (n << 1) >> 1] | 0;
                    b[x >> 1] = b[8180 + (n + 1 << 1) >> 1] | 0;
                    b[w >> 1] = b[8180 + (n + 2 << 1) >> 1] | 0;
                    b[g >> 1] = d;
                    n = B + 6 | 0;
                    m = B + 8 | 0;
                    v = B + 10 | 0;
                    s = e[n >> 1] | 0;
                    h = b[y + 6 >> 1] << 1;
                    r = e[m >> 1] | 0;
                    q = b[y + 8 >> 1] << 1;
                    p = e[v >> 1] | 0;
                    o = b[y + 10 >> 1] << 1;
                    k = 2147483647;
                    t = 0;
                    d = 0;
                    u = 9716;
                    while (1) {
                        l = (Z(h, s - (e[u >> 1] | 0) << 16 >> 16) | 0) >> 16;
                        l = Z(l, l) | 0;
                        c = (Z(q, r - (e[u + 2 >> 1] | 0) << 16 >> 16) | 0) >> 16;
                        l = (Z(c, c) | 0) + l | 0;
                        c = (Z(o, p - (e[u + 4 >> 1] | 0) << 16 >> 16) | 0) >> 16;
                        c = l + (Z(c, c) | 0) | 0;
                        l = (c | 0) < (k | 0);
                        d = l ? t : d;
                        t = t + 1 << 16 >> 16;
                        if (t << 16 >> 16 >= 512) break; else {
                            k = l ? c : k;
                            u = u + 6 | 0
                        }
                    }
                    k = (d << 16 >> 16) * 3 | 0;
                    b[n >> 1] = b[9716 + (k << 1) >> 1] | 0;
                    b[m >> 1] = b[9716 + (k + 1 << 1) >> 1] | 0;
                    b[v >> 1] = b[9716 + (k + 2 << 1) >> 1] | 0;
                    b[g + 2 >> 1] = d;
                    k = B + 12 | 0;
                    b[g + 4 >> 1] = ue(k, 12788, y + 12 | 0, 512) | 0;
                    t = x;
                    s = w;
                    d = v;
                    l = B;
                    break
                }
            } else {
                w = B + 2 | 0;
                x = B + 4 | 0;
                n = e[B >> 1] | 0;
                m = b[y >> 1] << 1;
                l = e[w >> 1] | 0;
                k = b[y + 2 >> 1] << 1;
                c = e[x >> 1] | 0;
                o = b[y + 4 >> 1] << 1;
                r = 2147483647;
                h = 0;
                d = 0;
                s = 8180;
                while (1) {
                    q = (Z(m, n - (e[s >> 1] | 0) << 16 >> 16) | 0) >> 16;
                    q = Z(q, q) | 0;
                    p = (Z(k, l - (e[s + 2 >> 1] | 0) << 16 >> 16) | 0) >> 16;
                    q = (Z(p, p) | 0) + q | 0;
                    p = (Z(o, c - (e[s + 4 >> 1] | 0) << 16 >> 16) | 0) >> 16;
                    p = q + (Z(p, p) | 0) | 0;
                    q = (p | 0) < (r | 0);
                    d = q ? h : d;
                    h = h + 1 << 16 >> 16;
                    if (h << 16 >> 16 >= 256) break; else {
                        r = q ? p : r;
                        s = s + 6 | 0
                    }
                }
                n = (d << 16 >> 16) * 3 | 0;
                b[B >> 1] = b[8180 + (n << 1) >> 1] | 0;
                b[w >> 1] = b[8180 + (n + 1 << 1) >> 1] | 0;
                b[x >> 1] = b[8180 + (n + 2 << 1) >> 1] | 0;
                b[g >> 1] = d;
                n = B + 6 | 0;
                m = B + 8 | 0;
                v = B + 10 | 0;
                s = e[n >> 1] | 0;
                h = b[y + 6 >> 1] << 1;
                r = e[m >> 1] | 0;
                q = b[y + 8 >> 1] << 1;
                p = e[v >> 1] | 0;
                o = b[y + 10 >> 1] << 1;
                k = 2147483647;
                t = 0;
                d = 0;
                u = 9716;
                while (1) {
                    l = (Z(h, s - (e[u >> 1] | 0) << 16 >> 16) | 0) >> 16;
                    l = Z(l, l) | 0;
                    c = (Z(q, r - (e[u + 2 >> 1] | 0) << 16 >> 16) | 0) >> 16;
                    l = (Z(c, c) | 0) + l | 0;
                    c = (Z(o, p - (e[u + 4 >> 1] | 0) << 16 >> 16) | 0) >> 16;
                    c = l + (Z(c, c) | 0) | 0;
                    l = (c | 0) < (k | 0);
                    d = l ? t : d;
                    t = t + 1 << 16 >> 16;
                    if (t << 16 >> 16 >= 256) break; else {
                        k = l ? c : k;
                        u = u + 12 | 0
                    }
                }
                k = (d << 16 >> 16) * 6 | 0;
                b[n >> 1] = b[9716 + (k << 1) >> 1] | 0;
                b[m >> 1] = b[9716 + ((k | 1) << 1) >> 1] | 0;
                b[v >> 1] = b[9716 + (k + 2 << 1) >> 1] | 0;
                b[g + 2 >> 1] = d;
                k = B + 12 | 0;
                b[g + 4 >> 1] = ue(k, 16884, y + 12 | 0, 128) | 0;
                t = w;
                s = x;
                d = v;
                l = B
            } while (0);
            u = a;
            p = B;
            o = u + 20 | 0;
            do {
                b[u >> 1] = b[p >> 1] | 0;
                u = u + 2 | 0;
                p = p + 2 | 0
            } while ((u | 0) < (o | 0));
            b[z >> 1] = (e[A >> 1] | 0) + (e[l >> 1] | 0);
            b[z + 2 >> 1] = (e[A + 2 >> 1] | 0) + (e[t >> 1] | 0);
            b[z + 4 >> 1] = (e[A + 4 >> 1] | 0) + (e[s >> 1] | 0);
            b[z + 6 >> 1] = (e[A + 6 >> 1] | 0) + (e[n >> 1] | 0);
            b[z + 8 >> 1] = (e[A + 8 >> 1] | 0) + (e[m >> 1] | 0);
            b[z + 10 >> 1] = (e[A + 10 >> 1] | 0) + (e[d >> 1] | 0);
            b[z + 12 >> 1] = (e[A + 12 >> 1] | 0) + (e[k >> 1] | 0);
            b[z + 14 >> 1] = (e[A + 14 >> 1] | 0) + (e[B + 14 >> 1] | 0);
            b[z + 16 >> 1] = (e[A + 16 >> 1] | 0) + (e[B + 16 >> 1] | 0);
            b[z + 18 >> 1] = (e[A + 18 >> 1] | 0) + (e[B + 18 >> 1] | 0);
            Ae(z, 205, 10, j);
            me(z, f, 10, j);
            i = C;
            return
        }

        function ue(a, c, d, f) {
            a = a | 0;
            c = c | 0;
            d = d | 0;
            f = f | 0;
            var g = 0, h = 0, i = 0, j = 0, k = 0, l = 0, m = 0, n = 0, o = 0, p = 0, q = 0, r = 0, s = 0, t = 0, u = 0,
                v = 0;
            t = a + 2 | 0;
            u = a + 4 | 0;
            v = a + 6 | 0;
            if (f << 16 >> 16 > 0) {
                m = e[a >> 1] | 0;
                n = b[d >> 1] << 1;
                o = e[t >> 1] | 0;
                p = b[d + 2 >> 1] << 1;
                q = e[u >> 1] | 0;
                r = b[d + 4 >> 1] << 1;
                s = e[v >> 1] | 0;
                g = b[d + 6 >> 1] << 1;
                j = 2147483647;
                k = 0;
                d = 0;
                l = c;
                while (1) {
                    h = (Z(n, m - (e[l >> 1] | 0) << 16 >> 16) | 0) >> 16;
                    h = Z(h, h) | 0;
                    i = (Z(p, o - (e[l + 2 >> 1] | 0) << 16 >> 16) | 0) >> 16;
                    h = (Z(i, i) | 0) + h | 0;
                    i = (Z(r, q - (e[l + 4 >> 1] | 0) << 16 >> 16) | 0) >> 16;
                    i = h + (Z(i, i) | 0) | 0;
                    h = (Z(g, s - (e[l + 6 >> 1] | 0) << 16 >> 16) | 0) >> 16;
                    h = i + (Z(h, h) | 0) | 0;
                    i = (h | 0) < (j | 0);
                    d = i ? k : d;
                    k = k + 1 << 16 >> 16;
                    if (k << 16 >> 16 >= f << 16 >> 16) break; else {
                        j = i ? h : j;
                        l = l + 8 | 0
                    }
                }
            } else d = 0;
            f = d << 16 >> 16 << 2;
            s = f | 1;
            b[a >> 1] = b[c + (f << 1) >> 1] | 0;
            b[t >> 1] = b[c + (s << 1) >> 1] | 0;
            b[u >> 1] = b[c + (s + 1 << 1) >> 1] | 0;
            b[v >> 1] = b[c + ((f | 3) << 1) >> 1] | 0;
            return d | 0
        }

        function ve(a, c, d, f, g, h, j) {
            a = a | 0;
            c = c | 0;
            d = d | 0;
            f = f | 0;
            g = g | 0;
            h = h | 0;
            j = j | 0;
            var k = 0, l = 0, m = 0, n = 0, o = 0, p = 0, q = 0, r = 0, s = 0, t = 0, u = 0, v = 0, w = 0, x = 0, y = 0,
                z = 0, A = 0, B = 0, C = 0, D = 0, E = 0, F = 0, G = 0, H = 0, I = 0, J = 0, K = 0;
            I = i;
            i = i + 192 | 0;
            m = I + 160 | 0;
            l = I + 140 | 0;
            C = I + 120 | 0;
            D = I + 100 | 0;
            E = I + 80 | 0;
            F = I + 60 | 0;
            k = I + 40 | 0;
            G = I + 20 | 0;
            H = I;
            ne(c, m, 10, j);
            ne(d, l, 10, j);
            fe(m, C, j);
            fe(l, D, j);
            n = 0;
            d = E;
            c = F;
            o = k;
            while (1) {
                B = (((b[a + (n << 1) >> 1] | 0) * 21299 | 0) >>> 15) + (e[20980 + (n << 1) >> 1] | 0) | 0;
                b[d >> 1] = B;
                b[c >> 1] = (e[m >> 1] | 0) - B;
                b[o >> 1] = (e[l >> 1] | 0) - B;
                n = n + 1 | 0;
                if ((n | 0) == 10) break; else {
                    m = m + 2 | 0;
                    l = l + 2 | 0;
                    d = d + 2 | 0;
                    c = c + 2 | 0;
                    o = o + 2 | 0
                }
            }
            b[h >> 1] = we(F, k, 21e3, b[C >> 1] | 0, b[C + 2 >> 1] | 0, b[D >> 1] | 0, b[D + 2 >> 1] | 0, 128) | 0;
            b[h + 2 >> 1] = we(F + 4 | 0, k + 4 | 0, 22024, b[C + 4 >> 1] | 0, b[C + 6 >> 1] | 0, b[D + 4 >> 1] | 0, b[D + 6 >> 1] | 0, 256) | 0;
            y = F + 8 | 0;
            z = k + 8 | 0;
            A = F + 10 | 0;
            B = k + 10 | 0;
            d = b[y >> 1] | 0;
            p = b[C + 8 >> 1] << 1;
            q = b[A >> 1] | 0;
            r = b[C + 10 >> 1] << 1;
            s = b[z >> 1] | 0;
            t = b[D + 8 >> 1] << 1;
            u = b[B >> 1] | 0;
            v = b[D + 10 >> 1] << 1;
            l = 2147483647;
            w = 0;
            o = 0;
            x = 24072;
            c = 0;
            while (1) {
                m = b[x >> 1] | 0;
                n = (Z(d - m << 16 >> 16, p) | 0) >> 16;
                n = Z(n, n) | 0;
                m = (Z(m + d << 16 >> 16, p) | 0) >> 16;
                m = Z(m, m) | 0;
                J = b[x + 2 >> 1] | 0;
                K = (Z(q - J << 16 >> 16, r) | 0) >> 16;
                n = (Z(K, K) | 0) + n | 0;
                J = (Z(J + q << 16 >> 16, r) | 0) >> 16;
                m = (Z(J, J) | 0) + m | 0;
                if ((n | 0) < (l | 0) | (m | 0) < (l | 0)) {
                    K = b[x + 4 >> 1] | 0;
                    J = (Z(s - K << 16 >> 16, t) | 0) >> 16;
                    J = (Z(J, J) | 0) + n | 0;
                    K = (Z(K + s << 16 >> 16, t) | 0) >> 16;
                    K = (Z(K, K) | 0) + m | 0;
                    m = b[x + 6 >> 1] | 0;
                    n = (Z(u - m << 16 >> 16, v) | 0) >> 16;
                    n = J + (Z(n, n) | 0) | 0;
                    m = (Z(m + u << 16 >> 16, v) | 0) >> 16;
                    m = K + (Z(m, m) | 0) | 0;
                    K = (n | 0) < (l | 0);
                    n = K ? n : l;
                    J = (m | 0) < (n | 0);
                    n = J ? m : n;
                    o = K | J ? w : o;
                    c = J ? 1 : K ? 0 : c
                } else n = l;
                w = w + 1 << 16 >> 16;
                if (w << 16 >> 16 >= 256) break; else {
                    l = n;
                    x = x + 8 | 0
                }
            }
            n = o << 16 >> 16;
            m = n << 2;
            o = m | 1;
            l = 24072 + (o << 1) | 0;
            d = b[24072 + (m << 1) >> 1] | 0;
            if (!(c << 16 >> 16)) {
                b[y >> 1] = d;
                b[A >> 1] = b[l >> 1] | 0;
                b[z >> 1] = b[24072 + (o + 1 << 1) >> 1] | 0;
                b[B >> 1] = b[24072 + ((m | 3) << 1) >> 1] | 0;
                c = n << 1
            } else {
                b[y >> 1] = 0 - (d & 65535);
                b[A >> 1] = 0 - (e[l >> 1] | 0);
                b[z >> 1] = 0 - (e[24072 + (o + 1 << 1) >> 1] | 0);
                b[B >> 1] = 0 - (e[24072 + ((m | 3) << 1) >> 1] | 0);
                c = n << 1 & 65534 | 1
            }
            b[h + 4 >> 1] = c;
            b[h + 6 >> 1] = we(F + 12 | 0, k + 12 | 0, 26120, b[C + 12 >> 1] | 0, b[C + 14 >> 1] | 0, b[D + 12 >> 1] | 0, b[D + 14 >> 1] | 0, 256) | 0;
            b[h + 8 >> 1] = we(F + 16 | 0, k + 16 | 0, 28168, b[C + 16 >> 1] | 0, b[C + 18 >> 1] | 0, b[D + 16 >> 1] | 0, b[D + 18 >> 1] | 0, 64) | 0;
            l = 0;
            m = G;
            n = H;
            d = E;
            c = F;
            while (1) {
                J = e[d >> 1] | 0;
                b[m >> 1] = J + (e[c >> 1] | 0);
                K = b[k >> 1] | 0;
                b[n >> 1] = J + (K & 65535);
                b[a + (l << 1) >> 1] = K;
                l = l + 1 | 0;
                if ((l | 0) == 10) break; else {
                    m = m + 2 | 0;
                    n = n + 2 | 0;
                    d = d + 2 | 0;
                    c = c + 2 | 0;
                    k = k + 2 | 0
                }
            }
            Ae(G, 205, 10, j);
            Ae(H, 205, 10, j);
            me(G, f, 10, j);
            me(H, g, 10, j);
            i = I;
            return
        }

        function we(a, c, d, e, f, g, h, i) {
            a = a | 0;
            c = c | 0;
            d = d | 0;
            e = e | 0;
            f = f | 0;
            g = g | 0;
            h = h | 0;
            i = i | 0;
            var j = 0, k = 0, l = 0, m = 0, n = 0, o = 0, p = 0, q = 0, r = 0, s = 0, t = 0, u = 0, v = 0, w = 0;
            o = b[a >> 1] | 0;
            u = a + 2 | 0;
            q = b[u >> 1] | 0;
            s = b[c >> 1] | 0;
            v = c + 2 | 0;
            t = b[v >> 1] | 0;
            if (i << 16 >> 16 > 0) {
                n = e << 16 >> 16 << 1;
                m = f << 16 >> 16 << 1;
                l = g << 16 >> 16 << 1;
                f = h << 16 >> 16 << 1;
                g = 2147483647;
                j = 0;
                e = 0;
                k = d;
                while (1) {
                    h = (Z(n, o - (b[k >> 1] | 0) | 0) | 0) >> 16;
                    h = Z(h, h) | 0;
                    if (((h | 0) < (g | 0) ? (p = (Z(m, q - (b[k + 2 >> 1] | 0) | 0) | 0) >> 16, p = (Z(p, p) | 0) + h | 0, (p | 0) < (g | 0)) : 0) ? (r = (Z(l, s - (b[k + 4 >> 1] | 0) | 0) | 0) >> 16, r = (Z(r, r) | 0) + p | 0, (r | 0) < (g | 0)) : 0) {
                        h = (Z(f, t - (b[k + 6 >> 1] | 0) | 0) | 0) >> 16;
                        h = (Z(h, h) | 0) + r | 0;
                        w = (h | 0) < (g | 0);
                        h = w ? h : g;
                        e = w ? j : e
                    } else h = g;
                    j = j + 1 << 16 >> 16;
                    if (j << 16 >> 16 >= i << 16 >> 16) break; else {
                        g = h;
                        k = k + 8 | 0
                    }
                }
            } else e = 0;
            w = e << 16 >> 16 << 2;
            i = w | 1;
            b[a >> 1] = b[d + (w << 1) >> 1] | 0;
            b[u >> 1] = b[d + (i << 1) >> 1] | 0;
            b[c >> 1] = b[d + (i + 1 << 1) >> 1] | 0;
            b[v >> 1] = b[d + ((w | 3) << 1) >> 1] | 0;
            return e | 0
        }

        function xe(a) {
            a = a | 0;
            var d = 0, e = 0, f = 0;
            if (!a) {
                f = -1;
                return f | 0
            }
            c[a >> 2] = 0;
            d = Je(20) | 0;
            if (!d) {
                f = -1;
                return f | 0
            }
            e = d;
            f = e + 20 | 0;
            do {
                b[e >> 1] = 0;
                e = e + 2 | 0
            } while ((e | 0) < (f | 0));
            c[a >> 2] = d;
            f = 0;
            return f | 0
        }

        function ye(a) {
            a = a | 0;
            var c = 0;
            if (!a) {
                c = -1;
                return c | 0
            }
            c = a + 20 | 0;
            do {
                b[a >> 1] = 0;
                a = a + 2 | 0
            } while ((a | 0) < (c | 0));
            c = 0;
            return c | 0
        }

        function ze(a) {
            a = a | 0;
            var b = 0;
            if (!a) return;
            b = c[a >> 2] | 0;
            if (!b) return;
            Ke(b);
            c[a >> 2] = 0;
            return
        }

        function Ae(a, c, d, e) {
            a = a | 0;
            c = c | 0;
            d = d | 0;
            e = e | 0;
            var f = 0, g = 0, h = 0;
            if (d << 16 >> 16 <= 0) return;
            f = c << 16 >> 16;
            g = c & 65535;
            h = 0;
            while (1) {
                e = b[a >> 1] | 0;
                if (e << 16 >> 16 < c << 16 >> 16) {
                    b[a >> 1] = c;
                    e = (c << 16 >> 16) + f | 0
                } else e = (e & 65535) + g | 0;
                h = h + 1 << 16 >> 16;
                if (h << 16 >> 16 >= d << 16 >> 16) break; else {
                    c = e & 65535;
                    a = a + 2 | 0
                }
            }
            return
        }

        function Be(a, c, d, e) {
            a = a | 0;
            c = c | 0;
            d = d | 0;
            e = e | 0;
            var f = 0, g = 0, h = 0, i = 0, j = 0, k = 0, l = 0, m = 0, n = 0, o = 0, p = 0, q = 0, r = 0, s = 0, t = 0;
            f = e << 16 >> 16;
            e = f >>> 2 & 65535;
            if (!(e << 16 >> 16)) return;
            n = f + -1 | 0;
            t = a + 20 | 0;
            p = c + (f + -4 << 1) | 0;
            q = c + (f + -3 << 1) | 0;
            r = c + (f + -2 << 1) | 0;
            s = c + (n << 1) | 0;
            o = c + (f + -11 << 1) | 0;
            n = d + (n << 1) | 0;
            while (1) {
                c = b[t >> 1] | 0;
                h = 5;
                i = t;
                j = o;
                k = o + -2 | 0;
                l = o + -4 | 0;
                m = o + -6 | 0;
                g = 2048;
                a = 2048;
                f = 2048;
                d = 2048;
                while (1) {
                    g = (Z(b[j >> 1] | 0, c) | 0) + g | 0;
                    a = (Z(b[k >> 1] | 0, c) | 0) + a | 0;
                    f = (Z(b[l >> 1] | 0, c) | 0) + f | 0;
                    c = (Z(b[m >> 1] | 0, c) | 0) + d | 0;
                    d = b[i + -2 >> 1] | 0;
                    g = g + (Z(b[j + 2 >> 1] | 0, d) | 0) | 0;
                    a = a + (Z(b[k + 2 >> 1] | 0, d) | 0) | 0;
                    f = f + (Z(b[l + 2 >> 1] | 0, d) | 0) | 0;
                    i = i + -4 | 0;
                    d = c + (Z(b[m + 2 >> 1] | 0, d) | 0) | 0;
                    h = h + -1 << 16 >> 16;
                    c = b[i >> 1] | 0;
                    if (!(h << 16 >> 16)) break; else {
                        j = j + 4 | 0;
                        k = k + 4 | 0;
                        l = l + 4 | 0;
                        m = m + 4 | 0
                    }
                }
                j = (Z(b[s >> 1] | 0, c) | 0) + g | 0;
                k = (Z(b[r >> 1] | 0, c) | 0) + a | 0;
                l = (Z(b[q >> 1] | 0, c) | 0) + f | 0;
                m = (Z(b[p >> 1] | 0, c) | 0) + d | 0;
                b[n >> 1] = j >>> 12;
                b[n + -2 >> 1] = k >>> 12;
                b[n + -4 >> 1] = l >>> 12;
                b[n + -6 >> 1] = m >>> 12;
                e = e + -1 << 16 >> 16;
                if (!(e << 16 >> 16)) break; else {
                    p = p + -8 | 0;
                    q = q + -8 | 0;
                    r = r + -8 | 0;
                    s = s + -8 | 0;
                    o = o + -8 | 0;
                    n = n + -8 | 0
                }
            }
            return
        }

        function Ce(a, b) {
            a = a | 0;
            b = b | 0;
            var d = 0;
            d = a + 32768 | 0;
            if ((a | 0) > -1 & (d ^ a | 0) < 0) {
                c[b >> 2] = 1;
                d = (a >>> 31) + 2147483647 | 0
            }
            return d >>> 16 & 65535 | 0
        }

        function De(a, b, d) {
            a = a | 0;
            b = b | 0;
            d = d | 0;
            var e = 0, f = 0;
            e = b << 16 >> 16;
            if (!(b << 16 >> 16)) return a | 0;
            if (b << 16 >> 16 > 0) {
                a = a << 16 >> 16 >> (b << 16 >> 16 > 15 ? 15 : e) & 65535;
                return a | 0
            }
            f = 0 - e | 0;
            b = a << 16 >> 16;
            f = (f & 65535) << 16 >> 16 > 15 ? 15 : f << 16 >> 16;
            e = b << f;
            if ((e << 16 >> 16 >> f | 0) == (b | 0)) {
                f = e & 65535;
                return f | 0
            }
            c[d >> 2] = 1;
            f = a << 16 >> 16 > 0 ? 32767 : -32768;
            return f | 0
        }

        function Ee(a, b, c) {
            a = a | 0;
            b = b | 0;
            c = c | 0;
            if (b << 16 >> 16 > 15) {
                b = 0;
                return b | 0
            }
            c = De(a, b, c) | 0;
            if (b << 16 >> 16 > 0) return c + ((1 << (b << 16 >> 16) + -1 & a << 16 >> 16 | 0) != 0 & 1) << 16 >> 16 | 0; else {
                b = c;
                return b | 0
            }
            return 0
        }

        function Fe(a, d, f) {
            a = a | 0;
            d = d | 0;
            f = f | 0;
            var g = 0, h = 0, i = 0;
            if ((a | 0) < 1) {
                b[d >> 1] = 0;
                f = 0;
                return f | 0
            }
            h = (pe(a) | 0) & 65534;
            i = h & 65535;
            h = h << 16 >> 16;
            if (i << 16 >> 16 > 0) {
                g = a << h;
                if ((g >> h | 0) != (a | 0)) g = a >> 31 ^ 2147483647
            } else {
                h = 0 - h << 16;
                if ((h | 0) < 2031616) g = a >> (h >> 16); else g = 0
            }
            b[d >> 1] = i;
            d = g >>> 25 & 63;
            d = d >>> 0 > 15 ? d + -16 | 0 : d;
            i = b[30216 + (d << 1) >> 1] | 0;
            a = i << 16;
            g = Z(i - (e[30216 + (d + 1 << 1) >> 1] | 0) << 16 >> 16, g >>> 10 & 32767) | 0;
            if ((g | 0) == 1073741824) {
                c[f >> 2] = 1;
                h = 2147483647
            } else h = g << 1;
            g = a - h | 0;
            if (((g ^ a) & (h ^ a) | 0) >= 0) {
                f = g;
                return f | 0
            }
            c[f >> 2] = 1;
            f = (i >>> 15 & 1) + 2147483647 | 0;
            return f | 0
        }

        function Ge(a, b, d) {
            a = a | 0;
            b = b | 0;
            d = d | 0;
            a = (a << 16 >> 16) - (b << 16 >> 16) | 0;
            if ((a + 32768 | 0) >>> 0 <= 65535) {
                d = a;
                d = d & 65535;
                return d | 0
            }
            c[d >> 2] = 1;
            d = (a | 0) > 32767 ? 32767 : -32768;
            d = d & 65535;
            return d | 0
        }

        function He(a, c, d, e, f, g) {
            a = a | 0;
            c = c | 0;
            d = d | 0;
            e = e | 0;
            f = f | 0;
            g = g | 0;
            var h = 0, j = 0, k = 0, l = 0, m = 0, n = 0, o = 0, p = 0, q = 0, r = 0, s = 0, t = 0, u = 0, v = 0, w = 0,
                x = 0, y = 0, z = 0, A = 0, B = 0, C = 0, D = 0;
            A = i;
            i = i + 48 | 0;
            o = A;
            k = o;
            h = f;
            j = k + 20 | 0;
            do {
                b[k >> 1] = b[h >> 1] | 0;
                k = k + 2 | 0;
                h = h + 2 | 0
            } while ((k | 0) < (j | 0));
            n = o + 18 | 0;
            s = a + 2 | 0;
            t = a + 4 | 0;
            p = c + 20 | 0;
            u = a + 6 | 0;
            v = a + 8 | 0;
            w = a + 10 | 0;
            x = a + 12 | 0;
            y = a + 14 | 0;
            z = a + 16 | 0;
            q = a + 18 | 0;
            r = a + 20 | 0;
            j = b[n >> 1] | 0;
            h = 5;
            l = c;
            m = d;
            k = o + 20 | 0;
            while (1) {
                D = b[a >> 1] | 0;
                C = (Z(D, b[l >> 1] | 0) | 0) + 2048 | 0;
                D = (Z(b[l + 2 >> 1] | 0, D) | 0) + 2048 | 0;
                o = j << 16 >> 16;
                C = C - (Z(o, b[s >> 1] | 0) | 0) | 0;
                B = b[t >> 1] | 0;
                o = D - (Z(o, B) | 0) | 0;
                D = b[n + -2 >> 1] | 0;
                B = C - (Z(D, B) | 0) | 0;
                C = b[u >> 1] | 0;
                D = o - (Z(C, D) | 0) | 0;
                o = b[n + -4 >> 1] | 0;
                C = B - (Z(o, C) | 0) | 0;
                B = b[v >> 1] | 0;
                o = D - (Z(B, o) | 0) | 0;
                D = b[n + -6 >> 1] | 0;
                B = C - (Z(D, B) | 0) | 0;
                C = b[w >> 1] | 0;
                D = o - (Z(D, C) | 0) | 0;
                o = b[n + -8 >> 1] | 0;
                C = B - (Z(o, C) | 0) | 0;
                B = b[x >> 1] | 0;
                o = D - (Z(B, o) | 0) | 0;
                D = b[n + -10 >> 1] | 0;
                B = C - (Z(D, B) | 0) | 0;
                C = b[y >> 1] | 0;
                D = o - (Z(C, D) | 0) | 0;
                o = b[n + -12 >> 1] | 0;
                C = B - (Z(o, C) | 0) | 0;
                B = b[z >> 1] | 0;
                o = D - (Z(o, B) | 0) | 0;
                D = b[n + -14 >> 1] | 0;
                B = C - (Z(D, B) | 0) | 0;
                C = b[q >> 1] | 0;
                D = o - (Z(C, D) | 0) | 0;
                o = b[n + -16 >> 1] | 0;
                C = B - (Z(o, C) | 0) | 0;
                B = b[r >> 1] | 0;
                o = D - (Z(B, o) | 0) | 0;
                B = C - (Z(b[n + -18 >> 1] | 0, B) | 0) | 0;
                B = (B + 134217728 | 0) >>> 0 < 268435455 ? B >>> 12 & 65535 : (B | 0) > 134217727 ? 32767 : -32768;
                o = o - (Z(b[s >> 1] | 0, B << 16 >> 16) | 0) | 0;
                n = k + 2 | 0;
                b[k >> 1] = B;
                b[m >> 1] = B;
                j = (o + 134217728 | 0) >>> 0 < 268435455 ? o >>> 12 & 65535 : (o | 0) > 134217727 ? 32767 : -32768;
                b[n >> 1] = j;
                b[m + 2 >> 1] = j;
                h = h + -1 << 16 >> 16;
                if (!(h << 16 >> 16)) break; else {
                    l = l + 4 | 0;
                    m = m + 4 | 0;
                    k = k + 4 | 0
                }
            }
            e = (e << 16 >> 16) + -10 | 0;
            k = e >>> 1 & 65535;
            if (k << 16 >> 16) {
                o = d + 18 | 0;
                j = c + 16 | 0;
                n = b[o >> 1] | 0;
                l = p;
                h = d + 20 | 0;
                while (1) {
                    B = b[a >> 1] | 0;
                    m = (Z(B, b[l >> 1] | 0) | 0) + 2048 | 0;
                    B = (Z(b[j + 6 >> 1] | 0, B) | 0) + 2048 | 0;
                    j = b[s >> 1] | 0;
                    C = n << 16 >> 16;
                    m = m - (Z(C, j) | 0) | 0;
                    D = b[t >> 1] | 0;
                    C = B - (Z(C, D) | 0) | 0;
                    B = b[o + -2 >> 1] | 0;
                    D = m - (Z(B, D) | 0) | 0;
                    m = b[u >> 1] | 0;
                    B = C - (Z(m, B) | 0) | 0;
                    C = b[o + -4 >> 1] | 0;
                    m = D - (Z(C, m) | 0) | 0;
                    D = b[v >> 1] | 0;
                    C = B - (Z(D, C) | 0) | 0;
                    B = b[o + -6 >> 1] | 0;
                    D = m - (Z(B, D) | 0) | 0;
                    m = b[w >> 1] | 0;
                    B = C - (Z(B, m) | 0) | 0;
                    C = b[o + -8 >> 1] | 0;
                    m = D - (Z(C, m) | 0) | 0;
                    D = b[x >> 1] | 0;
                    C = B - (Z(D, C) | 0) | 0;
                    B = b[o + -10 >> 1] | 0;
                    D = m - (Z(B, D) | 0) | 0;
                    m = b[y >> 1] | 0;
                    B = C - (Z(m, B) | 0) | 0;
                    C = b[o + -12 >> 1] | 0;
                    m = D - (Z(C, m) | 0) | 0;
                    D = b[z >> 1] | 0;
                    C = B - (Z(C, D) | 0) | 0;
                    B = b[o + -14 >> 1] | 0;
                    D = m - (Z(B, D) | 0) | 0;
                    m = b[q >> 1] | 0;
                    B = C - (Z(m, B) | 0) | 0;
                    C = b[o + -16 >> 1] | 0;
                    m = D - (Z(C, m) | 0) | 0;
                    D = b[r >> 1] | 0;
                    C = B - (Z(D, C) | 0) | 0;
                    D = m - (Z(b[o + -18 >> 1] | 0, D) | 0) | 0;
                    m = l + 4 | 0;
                    D = (D + 134217728 | 0) >>> 0 < 268435455 ? D >>> 12 & 65535 : (D | 0) > 134217727 ? 32767 : -32768;
                    j = C - (Z(j, D << 16 >> 16) | 0) | 0;
                    o = h + 2 | 0;
                    b[h >> 1] = D;
                    do if ((j + 134217728 | 0) >>> 0 >= 268435455) {//不可精简
                        h = h + 4 | 0;
                        if ((j | 0) > 134217727) {
                            b[o >> 1] = 32767;
                            j = 32767;
                            break
                        } else {
                            b[o >> 1] = -32768;
                            j = -32768;
                            break
                        }
                    } else {
                        j = j >>> 12 & 65535;
                        b[o >> 1] = j;
                        h = h + 4 | 0
                    } while (0);
                    k = k + -1 << 16 >> 16;
                    if (!(k << 16 >> 16)) break; else {
                        D = l;
                        n = j;
                        l = m;
                        j = D
                    }
                }
            }
            if (!(g << 16 >> 16)) {
                i = A;
                return
            }
            k = f;
            h = d + (e << 1) | 0;
            j = k + 20 | 0;
            do {
                b[k >> 1] = b[h >> 1] | 0;
                k = k + 2 | 0;
                h = h + 2 | 0
            } while ((k | 0) < (j | 0));
            i = A;
            return
        }

        function Ie(a, c, d) {
            a = a | 0;
            c = c | 0;
            d = d | 0;
            b[d >> 1] = b[a >> 1] | 0;
            b[d + 2 >> 1] = ((Z(b[c >> 1] | 0, b[a + 2 >> 1] | 0) | 0) + 16384 | 0) >>> 15;
            b[d + 4 >> 1] = ((Z(b[c + 2 >> 1] | 0, b[a + 4 >> 1] | 0) | 0) + 16384 | 0) >>> 15;
            b[d + 6 >> 1] = ((Z(b[c + 4 >> 1] | 0, b[a + 6 >> 1] | 0) | 0) + 16384 | 0) >>> 15;
            b[d + 8 >> 1] = ((Z(b[c + 6 >> 1] | 0, b[a + 8 >> 1] | 0) | 0) + 16384 | 0) >>> 15;
            b[d + 10 >> 1] = ((Z(b[c + 8 >> 1] | 0, b[a + 10 >> 1] | 0) | 0) + 16384 | 0) >>> 15;
            b[d + 12 >> 1] = ((Z(b[c + 10 >> 1] | 0, b[a + 12 >> 1] | 0) | 0) + 16384 | 0) >>> 15;
            b[d + 14 >> 1] = ((Z(b[c + 12 >> 1] | 0, b[a + 14 >> 1] | 0) | 0) + 16384 | 0) >>> 15;
            b[d + 16 >> 1] = ((Z(b[c + 14 >> 1] | 0, b[a + 16 >> 1] | 0) | 0) + 16384 | 0) >>> 15;
            b[d + 18 >> 1] = ((Z(b[c + 16 >> 1] | 0, b[a + 18 >> 1] | 0) | 0) + 16384 | 0) >>> 15;
            b[d + 20 >> 1] = ((Z(b[c + 18 >> 1] | 0, b[a + 20 >> 1] | 0) | 0) + 16384 | 0) >>> 15;
            return
        }

        function Je(a) {
            a = a | 0;
            var b = 0, d = 0, e = 0, f = 0, g = 0, h = 0, i = 0, j = 0, k = 0, l = 0, m = 0, n = 0, o = 0, p = 0, q = 0,
                r = 0, s = 0, t = 0, u = 0, v = 0, w = 0, x = 0, y = 0, z = 0, A = 0, B = 0, C = 0, D = 0, E = 0, F = 0,
                G = 0, H = 0, I = 0, J = 0, K = 0, L = 0, M = 0, N = 0, O = 0, P = 0, Q = 0, R = 0, S = 0, T = 0, U = 0,
                V = 0;
            do if (a >>> 0 < 245) {
                s = a >>> 0 < 11 ? 16 : a + 11 & -8;
                a = s >>> 3;
                m = c[26] | 0;
                j = m >>> a;
                if (j & 3) {
                    _abort();//fix cc 精简
                }
                b = c[28] | 0;
                if (s >>> 0 > b >>> 0) {
                    if (j) {
                        _abort();//fix cc 精简
                    }
                    a = c[27] | 0;
                    if (a) {
                        _abort();//fix cc 精简
                    } else V = 154
                } else V = 154
            } else if (a >>> 0 <= 4294967231) {
                a = a + 11 | 0;
                w = a & -8;
                m = c[27] | 0;
                if (m) {
                    _abort();//fix cc 精简
                } else {
                    s = w;
                    V = 154
                }
            } else {
                s = -1;
                V = 154
            } while (0);
            d:do if ((V | 0) == 154) {
                a = c[28] | 0;
                if (a >>> 0 >= s >>> 0) {
                    _abort();//fix cc 精简
                }
                a = c[29] | 0;
                if (a >>> 0 > s >>> 0) {
                    V = a - s | 0;
                    c[29] = V;
                    g = c[32] | 0;
                    c[32] = g + s;
                    c[g + (s + 4) >> 2] = V | 1;
                    c[g + 4 >> 2] = s | 3;
                    g = g + 8 | 0;
                    break
                }
                if (!(c[144] | 0)) Me();
                m = s + 48 | 0;
                d = c[146] | 0;
                l = s + 47 | 0;
                e = d + l | 0;
                d = 0 - d | 0;
                k = e & d;
                if (k >>> 0 > s >>> 0) {
                    a = c[136] | 0;
                    if ((a | 0) != 0 ? (C = c[134] | 0, H = C + k | 0, H >>> 0 <= C >>> 0 | H >>> 0 > a >>> 0) : 0) {
                        g = 0;
                        break
                    }
                    e:do if (!(c[137] & 4)) {
                        a = c[32] | 0;
                        f:do if (a) {
                            i = 552;
                            while (1) {
                                j = c[i >> 2] | 0;
                                if (j >>> 0 <= a >>> 0 ? (x = i + 4 | 0, (j + (c[x >> 2] | 0) | 0) >>> 0 > a >>> 0) : 0) {
                                    g = i;
                                    a = x;
                                    break
                                }
                                i = c[i + 8 >> 2] | 0;
                                if (!i) {
                                    V = 172;
                                    break f
                                }
                            }
                            j = e - (c[29] | 0) & d;
                            if (j >>> 0 < 2147483647) {
                                i = ga(j | 0) | 0;
                                H = (i | 0) == ((c[g >> 2] | 0) + (c[a >> 2] | 0) | 0);
                                a = H ? j : 0;
                                if (H) {
                                    if ((i | 0) != (-1 | 0)) {
                                        A = i;
                                        t = a;
                                        V = 192;
                                        break e
                                    }
                                } else V = 182
                            } else a = 0
                        } else V = 172; while (0);
                        do if ((V | 0) == 172) {
                            g = ga(0) | 0;
                            if ((g | 0) != (-1 | 0)) {
                                a = g;
                                j = c[145] | 0;
                                i = j + -1 | 0;
                                if (!(i & a)) j = k; else j = k - a + (i + a & 0 - j) | 0;
                                a = c[134] | 0;
                                i = a + j | 0;
                                if (j >>> 0 > s >>> 0 & j >>> 0 < 2147483647) {
                                    H = c[136] | 0;
                                    if ((H | 0) != 0 ? i >>> 0 <= a >>> 0 | i >>> 0 > H >>> 0 : 0) {
                                        a = 0;
                                        break
                                    }
                                    i = ga(j | 0) | 0;
                                    V = (i | 0) == (g | 0);
                                    a = V ? j : 0;
                                    if (V) {
                                        A = g;
                                        t = a;
                                        V = 192;
                                        break e
                                    } else V = 182
                                } else a = 0
                            } else a = 0
                        } while (0);
                        g:do if ((V | 0) == 182) {
                            _abort();//fix cc 精简
                        } while (0);
                        c[137] = c[137] | 4;
                        V = 189
                    } else {
                        a = 0;
                        V = 189
                    } while (0);
                    if ((((V | 0) == 189 ? k >>> 0 < 2147483647 : 0) ? (D = ga(k | 0) | 0, E = ga(0) | 0, D >>> 0 < E >>> 0 & ((D | 0) != (-1 | 0) & (E | 0) != (-1 | 0))) : 0) ? (F = E - D | 0, G = F >>> 0 > (s + 40 | 0) >>> 0, G) : 0) {
                        A = D;
                        t = G ? F : a;
                        V = 192
                    }
                    if ((V | 0) == 192) {
                        j = (c[134] | 0) + t | 0;
                        c[134] = j;
                        if (j >>> 0 > (c[135] | 0) >>> 0) c[135] = j;
                        q = c[32] | 0;
                        h:do if (q) {
                            g = 552;
                            do {
                                a = c[g >> 2] | 0;
                                j = g + 4 | 0;
                                i = c[j >> 2] | 0;
                                if ((A | 0) == (a + i | 0)) {
                                    I = a;
                                    J = j;
                                    K = i;
                                    L = g;
                                    V = 202;
                                    break
                                }
                                g = c[g + 8 >> 2] | 0
                            } while ((g | 0) != 0);
                            if (((V | 0) == 202 ? (c[L + 12 >> 2] & 8 | 0) == 0 : 0) ? q >>> 0 < A >>> 0 & q >>> 0 >= I >>> 0 : 0) {
                                c[J >> 2] = K + t;
                                V = (c[29] | 0) + t | 0;
                                U = q + 8 | 0;
                                U = (U & 7 | 0) == 0 ? 0 : 0 - U & 7;
                                T = V - U | 0;
                                c[32] = q + U;
                                c[29] = T;
                                c[q + (U + 4) >> 2] = T | 1;
                                c[q + (V + 4) >> 2] = 40;
                                c[33] = c[148];
                                break
                            }
                            j = c[30] | 0;
                            if (A >>> 0 < j >>> 0) {
                                c[30] = A;
                                j = A
                            }
                            i = A + t | 0;
                            a = 552;
                            while (1) {
                                if ((c[a >> 2] | 0) == (i | 0)) {
                                    _abort();//fix cc 精简
                                }
                                a = c[a + 8 >> 2] | 0;
                                if (!a) {
                                    i = 552;
                                    break
                                }
                            }
                            if ((V | 0) == 210) if (!(c[i + 12 >> 2] & 8)) {
                                _abort();//fix cc 精简
                            } else i = 552;
                            while (1) {
                                g = c[i >> 2] | 0;
                                if (g >>> 0 <= q >>> 0 ? (h = c[i + 4 >> 2] | 0, f = g + h | 0, f >>> 0 > q >>> 0) : 0) break;
                                i = c[i + 8 >> 2] | 0
                            }
                            i = g + (h + -39) | 0;
                            i = g + (h + -47 + ((i & 7 | 0) == 0 ? 0 : 0 - i & 7)) | 0;
                            j = q + 16 | 0;
                            i = i >>> 0 < j >>> 0 ? q : i;
                            h = i + 8 | 0;
                            g = A + 8 | 0;
                            g = (g & 7 | 0) == 0 ? 0 : 0 - g & 7;
                            V = t + -40 - g | 0;
                            c[32] = A + g;
                            c[29] = V;
                            c[A + (g + 4) >> 2] = V | 1;
                            c[A + (t + -36) >> 2] = 40;
                            c[33] = c[148];
                            g = i + 4 | 0;
                            c[g >> 2] = 27;
                            c[h >> 2] = c[138];
                            c[h + 4 >> 2] = c[139];
                            c[h + 8 >> 2] = c[140];
                            c[h + 12 >> 2] = c[141];
                            c[138] = A;
                            c[139] = t;
                            c[141] = 0;
                            c[140] = h;
                            h = i + 28 | 0;
                            c[h >> 2] = 7;
                            if ((i + 32 | 0) >>> 0 < f >>> 0) do {
                                _abort();//fix cc 精简
                            } while ((V + 8 | 0) >>> 0 < f >>> 0);
                            if ((i | 0) != (q | 0)) {
                                _abort();//fix cc 精简
                            }
                        } else {
                            V = c[30] | 0;
                            if ((V | 0) == 0 | A >>> 0 < V >>> 0) c[30] = A;
                            c[138] = A;
                            c[139] = t;
                            c[141] = 0;
                            c[35] = c[144];
                            c[34] = -1;
                            d = 0;
                            do {
                                V = d << 1;
                                U = 144 + (V << 2) | 0;
                                c[144 + (V + 3 << 2) >> 2] = U;
                                c[144 + (V + 2 << 2) >> 2] = U;
                                d = d + 1 | 0
                            } while ((d | 0) != 32);
                            V = A + 8 | 0;
                            V = (V & 7 | 0) == 0 ? 0 : 0 - V & 7;
                            U = t + -40 - V | 0;
                            c[32] = A + V;
                            c[29] = U;
                            c[A + (V + 4) >> 2] = U | 1;
                            c[A + (t + -36) >> 2] = 40;
                            c[33] = c[148]
                        } while (0);
                        b = c[29] | 0;
                        if (b >>> 0 > s >>> 0) {
                            V = b - s | 0;
                            c[29] = V;
                            g = c[32] | 0;
                            c[32] = g + s;
                            c[g + (s + 4) >> 2] = V | 1;
                            c[g + 4 >> 2] = s | 3;
                            g = g + 8 | 0;
                            break
                        }
                    }
                    c[(Le() | 0) >> 2] = 12;
                    g = 0
                } else g = 0
            } while (0);
            return g | 0
        }

        function Ke(a) {
            a = a | 0;
            var b = 0, d = 0, e = 0, f = 0, g = 0, h = 0, i = 0, j = 0, k = 0, l = 0, m = 0, n = 0, o = 0, p = 0, q = 0,
                r = 0, s = 0, t = 0, u = 0, v = 0, w = 0, x = 0, y = 0, z = 0, A = 0, B = 0;
            a:do if (a) {
                f = a + -8 | 0;
                k = c[30] | 0;
                b:do if (f >>> 0 >= k >>> 0 ? (e = c[a + -4 >> 2] | 0, d = e & 3, (d | 0) != 1) : 0) {
                    v = e & -8;
                    w = a + (v + -8) | 0;
                    do if (!(e & 1)) {
                        f = c[f >> 2] | 0;
                        if (!d) break a;
                        l = -8 - f | 0;
                        n = a + l | 0;
                        o = f + v | 0;
                        if (n >>> 0 < k >>> 0) break b;
                        if ((n | 0) == (c[31] | 0)) {
                            _abort();//fix cc 精简
                        }
                        d = f >>> 3;
                        if (f >>> 0 < 256) {
                            e = c[a + (l + 8) >> 2] | 0;
                            g = c[a + (l + 12) >> 2] | 0;
                            f = 144 + (d << 1 << 2) | 0;
                            do if ((e | 0) != (f | 0)) {
                                _abort();//fix cc 精简
                            } while (0);
                            if ((g | 0) == (e | 0)) {
                                c[26] = c[26] & ~(1 << d);
                                B = n;
                                g = o;
                                break
                            }
                            do if ((g | 0) == (f | 0)) b = g + 8 | 0; else {
                                _abort();//fix cc 精简
                            } while (0);
                            c[e + 12 >> 2] = g;
                            c[b >> 2] = e;
                            B = n;
                            g = o;
                            break
                        }
                        h = c[a + (l + 24) >> 2] | 0;
                        f = c[a + (l + 12) >> 2] | 0;
                        do if ((f | 0) == (n | 0)) {
                            e = a + (l + 20) | 0;
                            f = c[e >> 2] | 0;
                            if (!f) {
                                e = a + (l + 16) | 0;
                                f = c[e >> 2] | 0;
                                if (!f) {
                                    m = 0;
                                    break
                                }
                            }
                            while (1) {
                                d = f + 20 | 0;
                                b = c[d >> 2] | 0;
                                if (b) {
                                    f = b;
                                    e = d;
                                    continue
                                }
                                d = f + 16 | 0;
                                b = c[d >> 2] | 0;
                                if (!b) break; else {
                                    f = b;
                                    e = d
                                }
                            }
                            if (e >>> 0 < k >>> 0) ea(); else {
                                c[e >> 2] = 0;
                                m = f;
                                break
                            }
                        } else {
                            _abort();//fix cc 精简
                        } while (0);
                        if (h) {
                            f = c[a + (l + 28) >> 2] | 0;
                            e = 408 + (f << 2) | 0;
                            if ((n | 0) == (c[e >> 2] | 0)) {
                                c[e >> 2] = m;
                                if (!m) {
                                    c[27] = c[27] & ~(1 << f);
                                    B = n;
                                    g = o;
                                    break
                                }
                            } else {
                                if (h >>> 0 < (c[30] | 0) >>> 0) ea();
                                f = h + 16 | 0;
                                if ((c[f >> 2] | 0) == (n | 0)) c[f >> 2] = m; else c[h + 20 >> 2] = m;
                                if (!m) {
                                    B = n;
                                    g = o;
                                    break
                                }
                            }
                            e = c[30] | 0;
                            if (m >>> 0 < e >>> 0) ea();
                            c[m + 24 >> 2] = h;
                            f = c[a + (l + 16) >> 2] | 0;
                            do if (f) if (f >>> 0 < e >>> 0) ea(); else {
                                c[m + 16 >> 2] = f;
                                c[f + 24 >> 2] = m;
                                break
                            } while (0);
                            f = c[a + (l + 20) >> 2] | 0;
                            if (f) if (f >>> 0 < (c[30] | 0) >>> 0) ea(); else {
                                _abort();//fix cc 精简
                            } else {
                                B = n;
                                g = o
                            }
                        } else {
                            B = n;
                            g = o
                        }
                    } else {
                        B = f;
                        g = v
                    } while (0);
                    if (B >>> 0 < w >>> 0 ? (p = a + (v + -4) | 0, q = c[p >> 2] | 0, (q & 1 | 0) != 0) : 0) {
                        if (!(q & 2)) {
                            if ((w | 0) == (c[32] | 0)) {
                                A = (c[29] | 0) + g | 0;
                                c[29] = A;
                                c[32] = B;
                                c[B + 4 >> 2] = A | 1;
                                if ((B | 0) != (c[31] | 0)) break a;
                                c[31] = 0;
                                c[28] = 0;
                                break a
                            }
                            if ((w | 0) == (c[31] | 0)) {
                                _abort();//fix cc 精简
                            }
                            j = (q & -8) + g | 0;
                            d = q >>> 3;
                            do if (q >>> 0 >= 256) {
                                b = c[a + (v + 16) >> 2] | 0;
                                g = c[a + (v | 4) >> 2] | 0;
                                do if ((g | 0) == (w | 0)) {
                                    f = a + (v + 12) | 0;
                                    g = c[f >> 2] | 0;
                                    if (!g) {
                                        f = a + (v + 8) | 0;
                                        g = c[f >> 2] | 0;
                                        if (!g) {
                                            x = 0;
                                            break
                                        }
                                    }
                                    while (1) {
                                        e = g + 20 | 0;
                                        d = c[e >> 2] | 0;
                                        if (d) {
                                            g = d;
                                            f = e;
                                            continue
                                        }
                                        e = g + 16 | 0;
                                        d = c[e >> 2] | 0;
                                        if (!d) break; else {
                                            g = d;
                                            f = e
                                        }
                                    }
                                    if (f >>> 0 < (c[30] | 0) >>> 0) ea(); else {
                                        c[f >> 2] = 0;
                                        x = g;
                                        break
                                    }
                                } else {
                                    _abort();//fix cc 精简
                                } while (0);
                                if (b) {
                                    g = c[a + (v + 20) >> 2] | 0;
                                    f = 408 + (g << 2) | 0;
                                    if ((w | 0) == (c[f >> 2] | 0)) {
                                        c[f >> 2] = x;
                                        if (!x) {
                                            c[27] = c[27] & ~(1 << g);
                                            break
                                        }
                                    } else {
                                        if (b >>> 0 < (c[30] | 0) >>> 0) ea();
                                        g = b + 16 | 0;
                                        if ((c[g >> 2] | 0) == (w | 0)) c[g >> 2] = x; else c[b + 20 >> 2] = x;
                                        if (!x) break
                                    }
                                    g = c[30] | 0;
                                    if (x >>> 0 < g >>> 0) ea();
                                    c[x + 24 >> 2] = b;
                                    f = c[a + (v + 8) >> 2] | 0;
                                    do if (f) if (f >>> 0 < g >>> 0) ea(); else {
                                        _abort();//fix cc 精简
                                    } while (0);
                                    d = c[a + (v + 12) >> 2] | 0;
                                    if (d) if (d >>> 0 < (c[30] | 0) >>> 0) ea(); else {
                                        _abort();//fix cc 精简
                                    }
                                }
                            } else {
                                e = c[a + v >> 2] | 0;
                                g = c[a + (v | 4) >> 2] | 0;
                                f = 144 + (d << 1 << 2) | 0;
                                do if ((e | 0) != (f | 0)) {
                                    _abort();//fix cc 精简
                                } while (0);
                                if ((g | 0) == (e | 0)) {
                                    c[26] = c[26] & ~(1 << d);
                                    break
                                }
                                do if ((g | 0) == (f | 0)) r = g + 8 | 0; else {
                                    _abort();//fix cc 精简
                                } while (0);
                                c[e + 12 >> 2] = g;
                                c[r >> 2] = e
                            } while (0);
                            c[B + 4 >> 2] = j | 1;
                            c[B + j >> 2] = j;
                            if ((B | 0) == (c[31] | 0)) {
                                c[28] = j;
                                break a
                            } else g = j
                        } else {
                            c[p >> 2] = q & -2;
                            c[B + 4 >> 2] = g | 1;
                            c[B + g >> 2] = g
                        }
                        f = g >>> 3;
                        if (g >>> 0 < 256) {
                            e = f << 1;
                            g = 144 + (e << 2) | 0;
                            b = c[26] | 0;
                            d = 1 << f;
                            if (b & d) {
                                _abort();//fix cc 精简
                            } else {
                                c[26] = b | d;
                                y = 144 + (e + 2 << 2) | 0;
                                z = g
                            }
                            c[y >> 2] = B;
                            c[z + 12 >> 2] = B;
                            c[B + 8 >> 2] = z;
                            c[B + 12 >> 2] = g;
                            break a
                        }
                        b = g >>> 8;
                        if (b) if (g >>> 0 > 16777215) f = 31; else {
                            y = (b + 1048320 | 0) >>> 16 & 8;
                            z = b << y;
                            a = (z + 520192 | 0) >>> 16 & 4;
                            z = z << a;
                            f = (z + 245760 | 0) >>> 16 & 2;
                            f = 14 - (a | y | f) + (z << f >>> 15) | 0;
                            f = g >>> (f + 7 | 0) & 1 | f << 1
                        } else f = 0;
                        d = 408 + (f << 2) | 0;
                        c[B + 28 >> 2] = f;
                        c[B + 20 >> 2] = 0;
                        c[B + 16 >> 2] = 0;
                        b = c[27] | 0;
                        e = 1 << f;
                        c:do if (b & e) {
                            d = c[d >> 2] | 0;
                            d:do if ((c[d + 4 >> 2] & -8 | 0) != (g | 0)) {
                                f = g << ((f | 0) == 31 ? 0 : 25 - (f >>> 1) | 0);
                                while (1) {
                                    b = d + 16 + (f >>> 31 << 2) | 0;
                                    e = c[b >> 2] | 0;
                                    if (!e) break;
                                    if ((c[e + 4 >> 2] & -8 | 0) == (g | 0)) {
                                        A = e;
                                        break d
                                    } else {
                                        f = f << 1;
                                        d = e
                                    }
                                }
                                if (b >>> 0 < (c[30] | 0) >>> 0) ea(); else {
                                    c[b >> 2] = B;
                                    c[B + 24 >> 2] = d;
                                    c[B + 12 >> 2] = B;
                                    c[B + 8 >> 2] = B;
                                    break c
                                }
                            } else A = d; while (0);
                            b = A + 8 | 0;
                            d = c[b >> 2] | 0;
                            z = c[30] | 0;
                            if (d >>> 0 >= z >>> 0 & A >>> 0 >= z >>> 0) {
                                _abort();//fix cc 精简
                            } else ea()
                        } else {
                            c[27] = b | e;
                            c[d >> 2] = B;
                            c[B + 24 >> 2] = d;
                            c[B + 12 >> 2] = B;
                            c[B + 8 >> 2] = B
                        } while (0);
                        B = (c[34] | 0) + -1 | 0;
                        c[34] = B;
                        if (!B) b = 560; else break a;
                        while (1) {
                            b = c[b >> 2] | 0;
                            if (!b) break; else b = b + 8 | 0
                        }
                        c[34] = -1;
                        break a
                    }
                } while (0);
                ea()
            } while (0);
            return
        }

        function Le() {
            var a = 0;
            if (!0) a = 600; else a = c[(da() | 0) + 60 >> 2] | 0;
            return a | 0
        }

        function Me() {
            var a = 0;
            do if (!(c[144] | 0)) {
                a = ca(30) | 0;
                if (!(a + -1 & a)) {
                    c[146] = a;
                    c[145] = a;
                    c[147] = -1;
                    c[148] = -1;
                    c[149] = 0;
                    c[137] = 0;
                    c[144] = (ha(0) | 0) & -16 ^ 1431655768;
                    break
                } else ea()
            } while (0);
            return
        }

        //fix cc 精简

        function Oe(b, d, e) {
            b = b | 0;
            d = d | 0;
            e = e | 0;
            var f = 0;
            if ((e | 0) >= 4096) return ja(b | 0, d | 0, e | 0) | 0;
            f = b | 0;
            if ((b & 3) == (d & 3)) {
                while (b & 3) {
                    if (!e) return f | 0;
                    a[b >> 0] = a[d >> 0] | 0;
                    b = b + 1 | 0;
                    d = d + 1 | 0;
                    e = e - 1 | 0
                }
                while ((e | 0) >= 4) {
                    c[b >> 2] = c[d >> 2];
                    b = b + 4 | 0;
                    d = d + 4 | 0;
                    e = e - 4 | 0
                }
            }
            while ((e | 0) > 0) {
                a[b >> 0] = a[d >> 0] | 0;
                b = b + 1 | 0;
                d = d + 1 | 0;
                e = e - 1 | 0
            }
            return f | 0
        }

        function Pe(b, c, d) {
            b = b | 0;
            c = c | 0;
            d = d | 0;
            var e = 0;
            if ((c | 0) < (b | 0) & (b | 0) < (c + d | 0)) {
                _abort();//fix cc 精简
            } else Oe(b, c, d) | 0;
            return b | 0
        }

        function Qe(b, d, e) {
            b = b | 0;
            d = d | 0;
            e = e | 0;
            var f = 0, g = 0, h = 0, i = 0;
            f = b + e | 0;
            if ((e | 0) >= 20) {
                d = d & 255;
                h = b & 3;
                i = d | d << 8 | d << 16 | d << 24;
                g = f & ~3;
                if (h) {
                    h = b + 4 - h | 0;
                    while ((b | 0) < (h | 0)) {
                        a[b >> 0] = d;
                        b = b + 1 | 0
                    }
                }
                while ((b | 0) < (g | 0)) {
                    c[b >> 2] = i;
                    b = b + 4 | 0
                }
            }
            while ((b | 0) < (f | 0)) {
                a[b >> 0] = d;
                b = b + 1 | 0
            }
            return b - e | 0
        }

// EMSCRIPTEN_END_FUNCS
        return {
            _free: Ke,
            ___errno_location: Le,
            _memmove: Pe,
            _Decoder_Interface_Decode: xa,
            _Decoder_Interface_exit: wa,
            _Encoder_Interface_init: ya,
            _memset: Qe,
            _malloc: Je,
            _memcpy: Oe,
            _Encoder_Interface_exit: za,
            _Decoder_Interface_init: va,
            _Encoder_Interface_Encode: Aa //精简
        }
    })


    // EMSCRIPTEN_END_ASM
    (Module.asmGlobalArg, Module.asmLibraryArg, buffer);
    var _Encoder_Interface_Encode = Module["_Encoder_Interface_Encode"] = asm["_Encoder_Interface_Encode"];
    var _free = Module["_free"] = asm["_free"];
    var _memmove = Module["_memmove"] = asm["_memmove"];
    var _Decoder_Interface_exit = Module["_Decoder_Interface_exit"] = asm["_Decoder_Interface_exit"];
    var _Encoder_Interface_init = Module["_Encoder_Interface_init"] = asm["_Encoder_Interface_init"];
    var _memset = Module["_memset"] = asm["_memset"];
    var _malloc = Module["_malloc"] = asm["_malloc"];
    var _memcpy = Module["_memcpy"] = asm["_memcpy"];
    var _Decoder_Interface_Decode = Module["_Decoder_Interface_Decode"] = asm["_Decoder_Interface_Decode"];
    var _Decoder_Interface_init = Module["_Decoder_Interface_init"] = asm["_Decoder_Interface_init"];
    var _Encoder_Interface_exit = Module["_Encoder_Interface_exit"] = asm["_Encoder_Interface_exit"];
    var ___errno_location = Module["___errno_location"] = asm["___errno_location"];

	//精简
    Module["_main"]();
	
	AMR.Create=Create;
	return AMR;
};

Recorder.AMR=Create();

}));