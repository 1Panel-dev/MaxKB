<template>
    <div class="login-warp">
        <div class="login-container">
            <el-row class="container">
                <el-col :span="14" class="left-container">
                    <div class="login-image"></div>
                </el-col>
                <el-col :span="10" class="right-container">
                    <slot></slot>
                </el-col>

            </el-row>
        </div>

    </div>
</template>
<script setup lang="ts">


</script>
<style lang="scss" scope>
.login-warp {
    display: flex;
    align-items: center;
    justify-content: center;
    align-content: center;
    height: 100%;
    width: 100%;

    .login-container {
        width: 100%;
        height: 100%;

        .container {
            height: 100%;
            width: 100%;

            .right-container {
                display: flex;
                margin-top: 20vh;
                justify-content: center;
                width: 100%;
            }



            .left-container {
                .login-image {
                    background-image: url('@/assets/login.png');
                    background-size: 100% 100%;
                    width: 100%;
                    height: 100%;


                }
            }


        }


    }


}
</style>
