function copyValuetoClipboard(value){
    var textarea = document.createElement("textarea");
    textarea.textContent = value;
    textarea.style.position = "fixed";
    document.body.appendChild(textarea);
    textarea.select();
    try {
       return document.execCommand("copy");  // Security exception may be thrown by some browsers.
    } catch (ex) {
       console.warn("Copy to clipboard failed.", ex);
       return false;
    } finally {
       console.log("copied value: " + value)
       document.body.removeChild(textarea);
    }
}

function buildAndCopyRegex(_id, bossname, type){
  if (type == "attack"){
    copyValuetoClipboard("(14|15|16):" + _id + ":" + bossname)
  }else if(type == "debuff"){
    copyValuetoClipboard(":" + _id + ":" + bossname)
  }
}
