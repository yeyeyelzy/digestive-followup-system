<template>
  <div>
    <Aside></Aside>
    <chat></chat>
  </div>
</template>

<script>
import chat from "@/views/system/chat/index";
import Aside from "@/views/system/chat/aside";

export default {
  name: "chatlist",
  components:{
    chat,
    Aside
  }
}
</script>

<style scoped>

</style>
