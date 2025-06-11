/*
录音 Recorder扩展，音频变速变调转换，本代码从Sonic.java移植
https://github.com/xiangyuecn/Recorder

Recorder.Sonic(set)
Recorder.Sonic.Async(set)
	有两种构造方法：Sonic是同步方法，Sonic.Async是异步方法，同步方法简单直接但处理量大时会消耗大量时间，主要用于一次性的处理；异步方法由WebWorker在后台进行运算处理，但异步方法不一定能成功开启（低版本浏览器），主要用于实时处理。
	
	注意：异步方法调用后必须调用flush方法，否则会产生内存泄露。
	
【构造初始化参数】
	set:{
		sampleRate:待处理pcm的采样率，就是input输入的buffer的采样率
	}

【功能配置调用函数】同步异步通用，以下num取值正常为0.1-2.0，超过这个范围也是可以的，但不推荐
	.setPitch(num) num:0.1-n，变调不变速（会说话的汤姆猫），男女变声，只调整音调，不改变播放速度，默认为1.0不调整
	.setSpeed(num) num:0.1-n，变速不变调（快放慢放），只调整播放速度，不改变音调，默认为1.0不调整
	.setRate(num) num:0.1-n，变速变调，越小越缓重，越大越尖锐，会改变播放速度和音调，默认为1.0不调整
	.setVolume(num) num:0.1-n，调整音量，默认为1.0不调整
	.setChordPitch(bool) bool:默认false，作用未知，不推荐使用
	.setQuality(num) num:0或1，默认0时会减小输入采样率来提供处理速度，变调时才会用到，不推荐使用

【同步调用方法】
	.input(buffer) buffer:[Int16,...] 一维数组，输入pcm数据，返回转换后的部分pcm数据，完整输出需要调用flush；返回值[Int16,...]长度可能为0，代表没有数据被转换；此方法是耗时的方法，一次性处理大量pcm需要切片+setTimeout优化
	.flush() 将残余的未转换的pcm数据完成转换并返回；返回值[Int16,...]长度可能为0，代表没有数据被转换，flush后不能再调用input
【异步调用方法】
	.input(buffer,callback) callback:fn(pcm)，和同步方法相同，只是返回值通过callback返回
	.flush(callback) callback:fn(pcm)，和同步方法相同，只是返回值通过callback返回
*/
(function(factory){
	var browser=typeof window=="object" && !!window.document;
	var win=browser?window:Object; //非浏览器环境，Recorder挂载在Object下面
	var rec=win.Recorder,ni=rec.i18n;
	factory(rec,ni,ni.$T,browser);
}(function(Recorder,i18n,$T,isBrowser){
"use strict";

//是否支持web worker
var HasWebWorker=isBrowser && typeof Worker=="function";

function SonicFunction(SonicFunction_set){//用函数包裹方便Web Worker化

//暴露接口
var fn=function(set){
	this.set=set;
	
	var sonic=Sonic_Class(this);
	this.sonic=sonic;
	sonic.New(set.sampleRate,1);
};
fn.prototype=SonicFunction.prototype={
	input:function(buffer){
		this.sonic.writeShortToStream(buffer);
		return this.sonic.readShortFromStream();
	}
	,flush:function(){
		this.sonic.flushStream();
		return this.sonic.readShortFromStream();
	}
};



//java 兼容环境
var System={
	arraycopy:function(src,srcPos,dest,destPos,len){
		for(var i=0;i<len;i++){
			dest[destPos+i]=src[srcPos+i];
		};
	}
};


/* Sonic library
   Copyright 2010, 2011
   Bill Cox
   This file is part of the Sonic Library.

   This file is licensed under the Apache 2.0 license.
   
   https://github.com/waywardgeek/sonic/blob/71c51195de71627d7443d05378c680ba756545e8/Sonic.java
*/
//Sonic.java 转写 js
function Sonic_Class(FnObj) {

    var SONIC_MIN_PITCH = 65;
    var SONIC_MAX_PITCH = 400;
    // This is used to down-sample some inputs to improve speed
    var SONIC_AMDF_FREQ = 4000;
    // The number of points to use in the sinc FIR filter for resampling.
    var SINC_FILTER_POINTS = 12;
    var SINC_TABLE_SIZE = 601;

    // Lookup table for windowed sinc function of SINC_FILTER_POINTS points.
    var sincTable = [
        0, 0, 0, 0, 0, 0, 0, -1, -1, -2, -2, -3, -4, -6, -7, -9, -10, -12, -14,
        -17, -19, -21, -24, -26, -29, -32, -34, -37, -40, -42, -44, -47, -48, -50,
        -51, -52, -53, -53, -53, -52, -50, -48, -46, -43, -39, -34, -29, -22, -16,
        -8, 0, 9, 19, 29, 41, 53, 65, 79, 92, 107, 121, 137, 152, 168, 184, 200,
        215, 231, 247, 262, 276, 291, 304, 317, 328, 339, 348, 357, 363, 369, 372,
        374, 375, 373, 369, 363, 355, 345, 332, 318, 300, 281, 259, 234, 208, 178,
        147, 113, 77, 39, 0, -41, -85, -130, -177, -225, -274, -324, -375, -426,
        -478, -530, -581, -632, -682, -731, -779, -825, -870, -912, -951, -989,
        -1023, -1053, -1080, -1104, -1123, -1138, -1149, -1154, -1155, -1151,
        -1141, -1125, -1105, -1078, -1046, -1007, -963, -913, -857, -796, -728,
        -655, -576, -492, -403, -309, -210, -107, 0, 111, 225, 342, 462, 584, 708,
        833, 958, 1084, 1209, 1333, 1455, 1575, 1693, 1807, 1916, 2022, 2122, 2216,
        2304, 2384, 2457, 2522, 2579, 2625, 2663, 2689, 2706, 2711, 2705, 2687,
        2657, 2614, 2559, 2491, 2411, 2317, 2211, 2092, 1960, 1815, 1658, 1489,
        1308, 1115, 912, 698, 474, 241, 0, -249, -506, -769, -1037, -1310, -1586,
        -1864, -2144, -2424, -2703, -2980, -3254, -3523, -3787, -4043, -4291,
        -4529, -4757, -4972, -5174, -5360, -5531, -5685, -5819, -5935, -6029,
        -6101, -6150, -6175, -6175, -6149, -6096, -6015, -5905, -5767, -5599,
        -5401, -5172, -4912, -4621, -4298, -3944, -3558, -3141, -2693, -2214,
        -1705, -1166, -597, 0, 625, 1277, 1955, 2658, 3386, 4135, 4906, 5697, 6506,
        7332, 8173, 9027, 9893, 10769, 11654, 12544, 13439, 14335, 15232, 16128,
        17019, 17904, 18782, 19649, 20504, 21345, 22170, 22977, 23763, 24527,
        25268, 25982, 26669, 27327, 27953, 28547, 29107, 29632, 30119, 30569,
        30979, 31349, 31678, 31964, 32208, 32408, 32565, 32677, 32744, 32767,
        32744, 32677, 32565, 32408, 32208, 31964, 31678, 31349, 30979, 30569,
        30119, 29632, 29107, 28547, 27953, 27327, 26669, 25982, 25268, 24527,
        23763, 22977, 22170, 21345, 20504, 19649, 18782, 17904, 17019, 16128,
        15232, 14335, 13439, 12544, 11654, 10769, 9893, 9027, 8173, 7332, 6506,
        5697, 4906, 4135, 3386, 2658, 1955, 1277, 625, 0, -597, -1166, -1705,
        -2214, -2693, -3141, -3558, -3944, -4298, -4621, -4912, -5172, -5401,
        -5599, -5767, -5905, -6015, -6096, -6149, -6175, -6175, -6150, -6101,
        -6029, -5935, -5819, -5685, -5531, -5360, -5174, -4972, -4757, -4529,
        -4291, -4043, -3787, -3523, -3254, -2980, -2703, -2424, -2144, -1864,
        -1586, -1310, -1037, -769, -506, -249, 0, 241, 474, 698, 912, 1115, 1308,
        1489, 1658, 1815, 1960, 2092, 2211, 2317, 2411, 2491, 2559, 2614, 2657,
        2687, 2705, 2711, 2706, 2689, 2663, 2625, 2579, 2522, 2457, 2384, 2304,
        2216, 2122, 2022, 1916, 1807, 1693, 1575, 1455, 1333, 1209, 1084, 958, 833,
        708, 584, 462, 342, 225, 111, 0, -107, -210, -309, -403, -492, -576, -655,
        -728, -796, -857, -913, -963, -1007, -1046, -1078, -1105, -1125, -1141,
        -1151, -1155, -1154, -1149, -1138, -1123, -1104, -1080, -1053, -1023, -989,
        -951, -912, -870, -825, -779, -731, -682, -632, -581, -530, -478, -426,
        -375, -324, -274, -225, -177, -130, -85, -41, 0, 39, 77, 113, 147, 178,
        208, 234, 259, 281, 300, 318, 332, 345, 355, 363, 369, 373, 375, 374, 372,
        369, 363, 357, 348, 339, 328, 317, 304, 291, 276, 262, 247, 231, 215, 200,
        184, 168, 152, 137, 121, 107, 92, 79, 65, 53, 41, 29, 19, 9, 0, -8, -16,
        -22, -29, -34, -39, -43, -46, -48, -50, -52, -53, -53, -53, -52, -51, -50,
        -48, -47, -44, -42, -40, -37, -34, -32, -29, -26, -24, -21, -19, -17, -14,
        -12, -10, -9, -7, -6, -4, -3, -2, -2, -1, -1, 0, 0, 0, 0, 0, 0, 0
    ];

    var inputBuffer;
    var outputBuffer;
    var pitchBuffer;
    var downSampleBuffer;
    var speed=0;
    var volume=0;
    var pitch=0;
    var rate=0;
    var oldRatePosition=0;
    var newRatePosition=0;
    var useChordPitch=false;
    var quality=0;
    var numChannels=0;
    var inputBufferSize=0;
    var pitchBufferSize=0;
    var outputBufferSize=0;
    var numInputSamples=0;
    var numOutputSamples=0;
    var numPitchSamples=0;
    var minPeriod=0;
    var maxPeriod=0;
    var maxRequired=0;
    var remainingInputToCopy=0;
    var sampleRate=0;
    var prevPeriod=0;
    var prevMinDiff=0;
    var minDiff=0;
    var maxDiff=0;

    // Resize the array.
    function resize(
        oldArray,
        newLength)
    {
        newLength *= numChannels;
        var newArray = new Int16Array(newLength);
        var length = oldArray.length <= newLength? oldArray.length : newLength;

        System.arraycopy(oldArray, 0, newArray, 0, length);
        return newArray;
    }

    // Move samples from one array to another.  May move samples down within an array, but not up.
    function move(
        dest,
        destPos,
        source,
        sourcePos,
        numSamples)
    {
        System.arraycopy(source, sourcePos*numChannels, dest, destPos*numChannels, numSamples*numChannels);
    }

    // Scale the samples by the factor.
    function scaleSamples(
        samples,
        position,
        numSamples,
        volume)
    {
        var fixedPointVolume = Math.floor(volume*4096.0);
        var start = position*numChannels;
        var stop = start + numSamples*numChannels;

        for(var xSample = start; xSample < stop; xSample++) {
            var value = (samples[xSample]*fixedPointVolume) >> 12;
            if(value > 32767) {
                value = 32767;
            } else if(value < -32767) {
                value = -32767;
            }
            samples[xSample] = value;
        }
    }

    // Get the speed of the stream.
    function getSpeed()
    {
        return speed;
    }

    // Set the speed of the stream.
    function setSpeed(
        speed_)
    {
        speed = speed_;
    }

    // Get the pitch of the stream.
    function getPitch()
    {
        return pitch;
    }

    // Set the pitch of the stream.
    function setPitch(
        pitch_)
    {
        pitch = pitch_;
    }

    // Get the rate of the stream.
    function getRate()
    {
        return rate;
    }

    // Set the playback rate of the stream. This scales pitch and speed at the same time.
    function setRate(
        rate_)
    {
		if(rate!=rate_){//允许任意设置
			rate = rate_;
			oldRatePosition = 0;
			newRatePosition = 0;
		}
    }

    // Get the vocal chord pitch setting.
    function getChordPitch()
    {
        return useChordPitch;
    }

    // Set the vocal chord mode for pitch computation.  Default is off.
    function setChordPitch(
        useChordPitch_)
    {
        useChordPitch = useChordPitch_;
    }

    // Get the quality setting.
    function getQuality()
    {
        return quality;
    }

    // Set the "quality".  Default 0 is virtually as good as 1, but very much faster.
    function setQuality(
        quality_)
    {
        quality = quality_;
    }

    // Get the scaling factor of the stream.
    function getVolume()
    {
        return volume;
    }

    // Set the scaling factor of the stream.
    function setVolume(
        volume_)
    {
        volume = volume_;
    }

    // Allocate stream buffers.
    function allocateStreamBuffers(
        sampleRate_,
        numChannels_)
    {
        minPeriod = Math.floor(sampleRate_/SONIC_MAX_PITCH);
        maxPeriod = Math.floor(sampleRate_/SONIC_MIN_PITCH);
        maxRequired = 2*maxPeriod;
        inputBufferSize = maxRequired;
        inputBuffer = new Int16Array(maxRequired*numChannels_);
        outputBufferSize = maxRequired;
        outputBuffer = new Int16Array(maxRequired*numChannels_);
        pitchBufferSize = maxRequired;
        pitchBuffer = new Int16Array(maxRequired*numChannels_);
        downSampleBuffer = new Int16Array(maxRequired);
        sampleRate = sampleRate_;
        numChannels = numChannels_;
        oldRatePosition = 0;
        newRatePosition = 0;
        prevPeriod = 0;
    }

    // Create a sonic stream.
    function Sonic(
        sampleRate,
        numChannels)
    {
        allocateStreamBuffers(sampleRate, numChannels);
        speed = 1.0;
        pitch = 1.0;
        volume = 1.0;
        rate = 1.0;
        oldRatePosition = 0;
        newRatePosition = 0;
        useChordPitch = false;
        quality = 0;
    }

    // Get the sample rate of the stream.
    function getSampleRate()
    {
        return sampleRate;
    }

    // Set the sample rate of the stream.  This will cause samples buffered in the stream to be lost.
    function setSampleRate(
        sampleRate)
    {
        allocateStreamBuffers(sampleRate, numChannels);
    }

    // Get the number of channels.
    function getNumChannels()
    {
        return numChannels;
    }

    // Set the num channels of the stream.  This will cause samples buffered in the stream to be lost.
    function setNumChannels(
        numChannels)
    {
        allocateStreamBuffers(sampleRate, numChannels);
    }

    // Enlarge the output buffer if needed.
    function enlargeOutputBufferIfNeeded(
        numSamples)
    {
        if(numOutputSamples + numSamples > outputBufferSize) {
            outputBufferSize += (outputBufferSize >> 1) + numSamples;
            outputBuffer = resize(outputBuffer, outputBufferSize);
        }
    }

    // Enlarge the input buffer if needed.
    function enlargeInputBufferIfNeeded(
        numSamples)
    {
        if(numInputSamples + numSamples > inputBufferSize) {
            inputBufferSize += (inputBufferSize >> 1) + numSamples;
            inputBuffer = resize(inputBuffer, inputBufferSize);
        }
    }

    // Add the input samples to the input buffer.
    function addShortSamplesToInputBuffer(
        samples,
        numSamples)
    {
        if(numSamples == 0) {
            return;
        }
        enlargeInputBufferIfNeeded(numSamples);
        move(inputBuffer, numInputSamples, samples, 0, numSamples);
        numInputSamples += numSamples;
    }

    // Remove input samples that we have already processed.
    function removeInputSamples(
        position)
    {
        var remainingSamples = numInputSamples - position;

        move(inputBuffer, 0, inputBuffer, position, remainingSamples);
        numInputSamples = remainingSamples;
    }

    // Just copy from the array to the output buffer
    function copyToOutput(
        samples,
        position,
        numSamples)
    {
        enlargeOutputBufferIfNeeded(numSamples);
        move(outputBuffer, numOutputSamples, samples, position, numSamples);
        numOutputSamples += numSamples;
    }

    // Just copy from the input buffer to the output buffer.  Return num samples copied.
    function copyInputToOutput(
        position)
    {
        var numSamples = remainingInputToCopy;

        if(numSamples > maxRequired) {
            numSamples = maxRequired;
        }
        copyToOutput(inputBuffer, position, numSamples);
        remainingInputToCopy -= numSamples;
        return numSamples;
    }


    // Read short data out of the stream.  Sometimes no data will be available, and zero
    // is returned, which is not an error condition.
    function readShortFromStream() //已改成直接返回所有的Int16Array
    {
        var numSamples = numOutputSamples;
		var samples=new Int16Array(numSamples);
        var remainingSamples = 0;

        if(numSamples == 0) {
            return samples;
        }
        move(samples, 0, outputBuffer, 0, numSamples);
        move(outputBuffer, 0, outputBuffer, numSamples, remainingSamples);
        numOutputSamples = remainingSamples;
        return samples;
    }

    // Force the sonic stream to generate output using whatever data it currently
    // has.  No extra delay will be added to the output, but flushing in the middle of
    // words could introduce distortion.
    function flushStream()
    {
        var remainingSamples = numInputSamples;
        var s = speed/pitch;
        var r = rate*pitch;
        var expectedOutputSamples = Math.floor(numOutputSamples + Math.floor((remainingSamples/s + numPitchSamples)/r + 0.5));

        // Add enough silence to flush both input and pitch buffers.
        enlargeInputBufferIfNeeded(remainingSamples + 2*maxRequired);
        for(var xSample = 0; xSample < 2*maxRequired*numChannels; xSample++) {
            inputBuffer[remainingSamples*numChannels + xSample] = 0;
        }
        numInputSamples += 2*maxRequired;
        writeShortToStream(null, 0);
        // Throw away any extra samples we generated due to the silence we added.
        if(numOutputSamples > expectedOutputSamples) {
            numOutputSamples = expectedOutputSamples;
        }
        // Empty input and pitch buffers.
        numInputSamples = 0;
        remainingInputToCopy = 0;
        numPitchSamples = 0;
    }

    // Return the number of samples in the output buffer
    function samplesAvailable()
    {
        return numOutputSamples;
    }

    // If skip is greater than one, average skip samples together and write them to
    // the down-sample buffer.  If numChannels is greater than one, mix the channels
    // together as we down sample.
    function downSampleInput(
        samples,
        position,
        skip)
    {
        var numSamples = Math.floor(maxRequired/skip);
        var samplesPerValue = numChannels*skip;
        var value;

        position *= numChannels;
        for(var i = 0; i < numSamples; i++) {
            value = 0;
            for(var j = 0; j < samplesPerValue; j++) {
                value += samples[position + i*samplesPerValue + j];
            }
            value = Math.floor(value/samplesPerValue);
            downSampleBuffer[i] = value;
        }
    }

    // Find the best frequency match in the range, and given a sample skip multiple.
    // For now, just find the pitch of the first channel.
    function findPitchPeriodInRange(
        samples,
        position,
        minPeriod,
        maxPeriod)
    {
        var bestPeriod = 0, worstPeriod = 255;
        var minDiff_ = 1, maxDiff_ = 0;

        position *= numChannels;
        for(var period = minPeriod; period <= maxPeriod; period++) {
            var diff = 0;
            for(var i = 0; i < period; i++) {
                var sVal = samples[position + i];
                var pVal = samples[position + period + i];
                diff += sVal >= pVal? sVal - pVal : pVal - sVal;
            }
            /* Note that the highest number of samples we add into diff will be less
               than 256, since we skip samples.  Thus, diff is a 24 bit number, and
               we can safely multiply by numSamples without overflow */
            if(diff*bestPeriod < minDiff_*period) {
                minDiff_ = diff;
                bestPeriod = period;
            }
            if(diff*worstPeriod > maxDiff_*period) {
                maxDiff_ = diff;
                worstPeriod = period;
            }
        }
        minDiff = Math.floor(minDiff_/bestPeriod);
        maxDiff = Math.floor(maxDiff_/worstPeriod);

        return bestPeriod;
    }

    // At abrupt ends of voiced words, we can have pitch periods that are better
    // approximated by the previous pitch period estimate.  Try to detect this case.
    function prevPeriodBetter(
        minDiff,
        maxDiff,
        preferNewPeriod)
    {
        if(minDiff == 0 || prevPeriod == 0) {
            return false;
        }
        if(preferNewPeriod) {
            if(maxDiff > minDiff*3) {
                // Got a reasonable match this period
                return false;
            }
            if(minDiff*2 <= prevMinDiff*3) {
                // Mismatch is not that much greater this period
                return false;
            }
        } else {
            if(minDiff <= prevMinDiff) {
                return false;
            }
        }
        return true;
    }

    // Find the pitch period.  This is a critical step, and we may have to try
    // multiple ways to get a good answer.  This version uses AMDF.  To improve
    // speed, we down sample by an integer factor get in the 11KHz range, and then
    // do it again with a narrower frequency range without down sampling
    function findPitchPeriod(
        samples,
        position,
        preferNewPeriod)
    {
        var period, retPeriod;
        var skip = 1;

        if(sampleRate > SONIC_AMDF_FREQ && quality == 0) {
            skip = Math.floor(sampleRate/SONIC_AMDF_FREQ);
        }
        if(numChannels == 1 && skip == 1) {
            period = findPitchPeriodInRange(samples, position, minPeriod, maxPeriod);
        } else {
            downSampleInput(samples, position, skip);
            period = findPitchPeriodInRange(downSampleBuffer, 0, Math.floor(minPeriod/skip),
                Math.floor(maxPeriod/skip));
            if(skip != 1) {
                period *= skip;
                var minP = period - (skip << 2);
                var maxP = period + (skip << 2);
                if(minP < minPeriod) {
                    minP = minPeriod;
                }
                if(maxP > maxPeriod) {
                    maxP = maxPeriod;
                }
                if(numChannels == 1) {
                    period = findPitchPeriodInRange(samples, position, minP, maxP);
                } else {
                    downSampleInput(samples, position, 1);
                    period = findPitchPeriodInRange(downSampleBuffer, 0, minP, maxP);
                }
            }
        }
        if(prevPeriodBetter(minDiff, maxDiff, preferNewPeriod)) {
            retPeriod = prevPeriod;
        } else {
            retPeriod = period;
        }
        prevMinDiff = minDiff;
        prevPeriod = period;
        return retPeriod;
    }

    // Overlap two sound segments, ramp the volume of one down, while ramping the
    // other one from zero up, and add them, storing the result at the output.
    function overlapAdd(
        numSamples,
        numChannels,
        out,
        outPos,
        rampDown,
        rampDownPos,
        rampUp,
        rampUpPos)
    {
         for(var i = 0; i < numChannels; i++) {
            var o = outPos*numChannels + i;
            var u = rampUpPos*numChannels + i;
            var d = rampDownPos*numChannels + i;
            for(var t = 0; t < numSamples; t++) {
                out[o] = Math.floor((rampDown[d]*(numSamples - t) + rampUp[u]*t)/numSamples);
                o += numChannels;
                d += numChannels;
                u += numChannels;
            }
        }
    }

    // Overlap two sound segments, ramp the volume of one down, while ramping the
    // other one from zero up, and add them, storing the result at the output.
    function overlapAddWithSeparation(
        numSamples,
        numChannels,
        separation,
        out,
        outPos,
        rampDown,
        rampDownPos,
        rampUp,
        rampUpPos)
    {
        for(var i = 0; i < numChannels; i++) {
            var o = outPos*numChannels + i;
            var u = rampUpPos*numChannels + i;
            var d = rampDownPos*numChannels + i;
            for(var t = 0; t < numSamples + separation; t++) {
                if(t < separation) {
                    out[o] = Math.floor(rampDown[d]*(numSamples - t)/numSamples);
                    d += numChannels;
                } else if(t < numSamples) {
                    out[o] = Math.floor((rampDown[d]*(numSamples - t) + rampUp[u]*(t - separation))/numSamples);
                    d += numChannels;
                    u += numChannels;
                } else {
                    out[o] = Math.floor(rampUp[u]*(t - separation)/numSamples);
                    u += numChannels;
                }
                o += numChannels;
            }
        }
    }

    // Just move the new samples in the output buffer to the pitch buffer
    function moveNewSamplesToPitchBuffer(
        originalNumOutputSamples)
    {
        var numSamples = numOutputSamples - originalNumOutputSamples;

        if(numPitchSamples + numSamples > pitchBufferSize) {
            pitchBufferSize += (pitchBufferSize >> 1) + numSamples;
            pitchBuffer = resize(pitchBuffer, pitchBufferSize);
        }
        move(pitchBuffer, numPitchSamples, outputBuffer, originalNumOutputSamples, numSamples);
        numOutputSamples = originalNumOutputSamples;
        numPitchSamples += numSamples;
    }

    // Remove processed samples from the pitch buffer.
    function removePitchSamples(
        numSamples)
    {
        if(numSamples == 0) {
            return;
        }
        move(pitchBuffer, 0, pitchBuffer, numSamples, numPitchSamples - numSamples);
        numPitchSamples -= numSamples;
    }

    // Change the pitch.  The latency this introduces could be reduced by looking at
    // past samples to determine pitch, rather than future.
    function adjustPitch(
        originalNumOutputSamples)
    {
        var period, newPeriod, separation;
        var position = 0;

        if(numOutputSamples == originalNumOutputSamples) {
            return;
        }
        moveNewSamplesToPitchBuffer(originalNumOutputSamples);
        while(numPitchSamples - position >= maxRequired) {
            period = findPitchPeriod(pitchBuffer, position, false);
            newPeriod = Math.floor(period/pitch);
            enlargeOutputBufferIfNeeded(newPeriod);
            if(pitch >= 1.0) {
                overlapAdd(newPeriod, numChannels, outputBuffer, numOutputSamples, pitchBuffer,
                        position, pitchBuffer, position + period - newPeriod);
            } else {
                separation = newPeriod - period;
                overlapAddWithSeparation(period, numChannels, separation, outputBuffer, numOutputSamples,
                        pitchBuffer, position, pitchBuffer, position);
            }
            numOutputSamples += newPeriod;
            position += period;
        }
        removePitchSamples(position);
    }

    // Aproximate the sinc function times a Hann window from the sinc table.
    function findSincCoefficient(i, ratio, width) {
        var lobePoints = Math.floor((SINC_TABLE_SIZE-1)/SINC_FILTER_POINTS);
        var left = Math.floor(i*lobePoints + (ratio*lobePoints)/width);
        var right = left + 1;
        var position = i*lobePoints*width + ratio*lobePoints - left*width;
        var leftVal = sincTable[left];
        var rightVal = sincTable[right];

        return Math.floor(((leftVal*(width - position) + rightVal*position) << 1)/width);
    }

    // Return 1 if value >= 0, else -1.  This represents the sign of value.
    function getSign(value) {
        return value >= 0? 1 : -1;
    }

    // Interpolate the new output sample.
    function interpolate(
        in_,
        inPos,  // Index to first sample which already includes channel offset.
        oldSampleRate,
        newSampleRate)
    {
        // Compute N-point sinc FIR-filter here.  Clip rather than overflow.
        var i;
        var total = 0;
        var position = newRatePosition*oldSampleRate;
        var leftPosition = oldRatePosition*newSampleRate;
        var rightPosition = (oldRatePosition + 1)*newSampleRate;
        var ratio = rightPosition - position - 1;
        var width = rightPosition - leftPosition;
        var weight, value;
        var oldSign;
        var overflowCount = 0;

        for (i = 0; i < SINC_FILTER_POINTS; i++) {
            weight = findSincCoefficient(i, ratio, width);
            /* printf("%u %f\n", i, weight); */
            value = in_[inPos + i*numChannels]*weight;
            oldSign = getSign(total);
            total += value;
            if (oldSign != getSign(total) && getSign(value) == oldSign) {
                /* We must have overflowed.  This can happen with a sinc filter. */
                overflowCount += oldSign;
            }
        }
        /* It is better to clip than to wrap if there was a overflow. */
        if (overflowCount > 0) {
            return 0x7FFF;
        } else if (overflowCount < 0) {
            return -0x8000;
        }
        return (total >> 16)&0xffff;
    }

    // Change the rate.
    function adjustRate(
        rate,
        originalNumOutputSamples)
    {
        var newSampleRate = Math.floor(sampleRate/rate);
        var oldSampleRate = sampleRate;
        var position;

        // Set these values to help with the integer math
        while(newSampleRate > (1 << 14) || oldSampleRate > (1 << 14)) {
            newSampleRate >>= 1;
            oldSampleRate >>= 1;
        }
        if(numOutputSamples == originalNumOutputSamples) {
            return;
        }
        moveNewSamplesToPitchBuffer(originalNumOutputSamples);
        // Leave at least one pitch sample in the buffer
        for(position = 0; position < numPitchSamples - 1; position++) {
            while((oldRatePosition + 1)*newSampleRate > newRatePosition*oldSampleRate) {
                enlargeOutputBufferIfNeeded(1);
                for(var i = 0; i < numChannels; i++) {
                    outputBuffer[numOutputSamples*numChannels + i] = interpolate(pitchBuffer,
                            position*numChannels + i, oldSampleRate, newSampleRate);
                }
                newRatePosition++;
                numOutputSamples++;
            }
            oldRatePosition++;
            if(oldRatePosition == oldSampleRate) {
                oldRatePosition = 0;
                if(newRatePosition != newSampleRate) {
                    throw new Error("Assertion failed: newRatePosition != newSampleRate\n");
                    //assert false;
                }
                newRatePosition = 0;
            }
        }
        removePitchSamples(position);
    }


    // Skip over a pitch period, and copy period/speed samples to the output
    function skipPitchPeriod(
        samples,
        position,
        speed,
        period)
    {
        var newSamples;

        if(speed >= 2.0) {
            newSamples = Math.floor(period/(speed - 1.0));
        } else {
            newSamples = period;
            remainingInputToCopy = Math.floor(period*(2.0 - speed)/(speed - 1.0));
        }
        enlargeOutputBufferIfNeeded(newSamples);
        overlapAdd(newSamples, numChannels, outputBuffer, numOutputSamples, samples, position,
                samples, position + period);
        numOutputSamples += newSamples;
        return newSamples;
    }

    // Insert a pitch period, and determine how much input to copy directly.
    function insertPitchPeriod(
        samples,
        position,
        speed,
        period)
    {
        var newSamples;

        if(speed < 0.5) {
            newSamples = Math.floor(period*speed/(1.0 - speed));
        } else {
            newSamples = period;
            remainingInputToCopy = Math.floor(period*(2.0*speed - 1.0)/(1.0 - speed));
        }
        enlargeOutputBufferIfNeeded(period + newSamples);
        move(outputBuffer, numOutputSamples, samples, position, period);
        overlapAdd(newSamples, numChannels, outputBuffer, numOutputSamples + period, samples,
                position + period, samples, position);
        numOutputSamples += period + newSamples;
        return newSamples;
    }

    // Resample as many pitch periods as we have buffered on the input.  Return 0 if
    // we fail to resize an input or output buffer.  Also scale the output by the volume.
    function changeSpeed(
        speed)
    {
        var numSamples = numInputSamples;
        var position = 0, period, newSamples;

        if(numInputSamples < maxRequired) {
            return;
        }
        do {
            if(remainingInputToCopy > 0) {
                newSamples = copyInputToOutput(position);
                position += newSamples;
            } else {
                period = findPitchPeriod(inputBuffer, position, true);
                if(speed > 1.0) {
                    newSamples = skipPitchPeriod(inputBuffer, position, speed, period);
                    position += period + newSamples;
                } else {
                    newSamples = insertPitchPeriod(inputBuffer, position, speed, period);
                    position += newSamples;
                }
            }
        } while(position + maxRequired <= numSamples);
        removeInputSamples(position);
    }

    // Resample as many pitch periods as we have buffered on the input.  Scale the output by the volume.
    function processStreamInput()
    {
        var originalNumOutputSamples = numOutputSamples;
        var s = speed/pitch;
        var r = rate;

        if(!useChordPitch) {
            r *= pitch;
        }
        if(s > 1.00001 || s < 0.99999) {
            changeSpeed(s);
        } else {
            copyToOutput(inputBuffer, 0, numInputSamples);
            numInputSamples = 0;
        }
        if(useChordPitch) {
            if(pitch != 1.0) {
                adjustPitch(originalNumOutputSamples);
            }
        } else if(r != 1.0) {
            adjustRate(r, originalNumOutputSamples);
        }
        if(volume != 1.0) {
            // Adjust output volume.
            scaleSamples(outputBuffer, originalNumOutputSamples, numOutputSamples - originalNumOutputSamples,
                volume);
        }
    }

    // Write the data to the input stream, and process it.
    function writeShortToStream(
        samples)
    {
        addShortSamplesToInputBuffer(samples, samples?samples.length:0);
        processStreamInput();
    }

	
	
	
	/**导出Sonic对象**/
	FnObj.setPitch=setPitch;
	FnObj.setRate=setRate;
	FnObj.setSpeed=setSpeed;
	FnObj.setVolume=setVolume;
	FnObj.setChordPitch=setChordPitch;
	FnObj.setQuality=setQuality;
	return {
		New:Sonic
		
		,flushStream:flushStream
		,writeShortToStream:writeShortToStream
		,readShortFromStream:readShortFromStream
	};
}

return new fn(SonicFunction_set);
};










Recorder.Sonic=SonicFunction;

//Worker异步化
var sonicWorker;
Recorder.BindDestroy("sonicWorker",function(){
	if(sonicWorker){
		Recorder.CLog("sonicWorker Destroy");
		sonicWorker&&sonicWorker.terminate();
		sonicWorker=null;
	};
});
//开启异步，如果返回null代表不支持，开启成功后必须调用flush方法，否则会内存泄露
var openList={id:0};
SonicFunction.Async=function(set){
	if(!HasWebWorker){
		Recorder.CLog($T("Ikdz::当前环境不支持Web Worker，不支持调用Sonic.Async"),3);
		return null;
	};
	var worker=sonicWorker;
	try{
		var onmsg=function(e){
			var ed=e.data;
			var cur=wk_ctxs[ed.id];
			if(ed.action=="init"){
				wk_ctxs[ed.id]={
					sampleRate:ed.sampleRate
					
					,sonicObj:wk_sonic({sampleRate:ed.sampleRate})
				};
			}else if(!cur){
				return;
			};
			
			switch(ed.action){
			case "flush":
				var pcm=cur.sonicObj.flush();
				self.postMessage({
					action:ed.action
					,id:ed.id
					,call:ed.call
					,pcm:pcm
				});
				
				cur.sonicObj=null;
				delete wk_ctxs[ed.id];
				break;
			case "input":
				var pcm=cur.sonicObj.input(ed.pcm);
				self.postMessage({
					action:ed.action
					,id:ed.id
					,call:ed.call
					,pcm:pcm
				});
				break;
			default:
				if(/^set/.test(ed.action)){
					cur.sonicObj[ed.action](ed.param);
				};
			};
		};
		if(!worker){
			//创建一个新Worker
			var jsCode=");var wk_ctxs={};self.onmessage="+onmsg;
			
			var sonicCode=Recorder.Sonic.toString();
			var url=(window.URL||webkitURL).createObjectURL(new Blob(["var wk_sonic=(",sonicCode,jsCode], {type:"text/javascript"}));
			
			worker=new Worker(url);
			setTimeout(function(){
				(window.URL||webkitURL).revokeObjectURL(url);//必须要释放，不然每次调用内存都明显泄露内存
			},10000);//chrome 83 file协议下如果直接释放，将会使WebWorker无法启动
			
			worker.onmessage=function(e){
				var ctx=openList[e.data.id];
				if(ctx){
					var fn=ctx.cbs[e.data.call];
					fn&&fn(e.data);
				};
			};
		};
		
		var ctx=new sonicWorkerCtx(worker,set);
		ctx.id=++openList.id;
		openList[ctx.id]=ctx;
		
		worker.postMessage({
			action:"init"
			,id:ctx.id
			,sampleRate:set.sampleRate
			
			,x:new Int16Array(5)//低版本浏览器不支持序列化TypedArray
		});
		
		
		sonicWorker=worker;
		return ctx;
	}catch(e){//出错了就不要提供了
		worker&&worker.terminate();
		
		console.error(e);
		return null;
	};
};

var sonicWorkerCtx=function(worker,set){
	this.worker=worker;
	this.set=set;
	
	this.cbs={i:0};
};
sonicWorkerCtx.prototype={
	cb:function(call){
		var This=this;
		var id="cb"+(++This.cbs.i);
		This.cbs[id]=function(data){
			delete This.cbs[id];
			call(data);
		};
		return id;
	}
	,flush:function(call){
		var This=this;if(!This.worker)return;
		
		This.worker.postMessage({
			action:"flush"
			,id:This.id
			,call:This.cb(function(data){
				call&&call(data.pcm);
				
				This.worker=null;
				delete openList[This.id];
				
				//疑似泄露检测 排除id
				var opens=-1;
				for(var k in openList){
					opens++;
				};
				if(opens){
					Recorder.CLog($T("IC5Y::sonic worker剩{1}个未flush",0,opens),3);
				};
			})
		});
	}
	,input:function(pcm,call){
		var This=this;if(!This.worker)return;
		
		This.worker.postMessage({
			action:"input"
			,id:This.id
			,pcm:pcm
			,call:This.cb(function(data){
				call&&call(data.pcm);
			})
		});
	}
};
var addWorkerCtxSet=function(key){
	sonicWorkerCtx.prototype[key]=function(param){
		var This=this;if(!This.worker)return;
		
		This.worker.postMessage({
			action:key
			,id:This.id
			,param:param
		});
	}
};
addWorkerCtxSet("setPitch");
addWorkerCtxSet("setRate");
addWorkerCtxSet("setSpeed");
addWorkerCtxSet("setVolume");
addWorkerCtxSet("setChordPitch");
addWorkerCtxSet("setQuality");

}));