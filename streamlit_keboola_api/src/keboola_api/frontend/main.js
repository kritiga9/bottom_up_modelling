
function sendValue(value) {
  Streamlit.setComponentValue(value)
}

function getParentElement()   {
  var ifs = window.top.document.getElementsByTagName("iframe");
  for(var i = 0, len = ifs.length; i < len; i++)  {
     var f = ifs[i];
     var fDoc = f.contentDocument || f.contentWindow.document;
     if(fDoc === document)   {
        return f.parentElement
     }
  }
}

function onRender(event) {
    const {label,key,api_only} = event.detail.args;
    if(api_only==true){
      if (!window.rendered) {
        sendValue(Math.random()*1000);
        Streamlit.setFrameHeight(0);
        getParentElement().style.height="0px";
      }
    }
    else{
      document.getElementById("root").style.display='block'
      var upload = document.getElementById("upload");
      upload.textContent=label;
      upload.onclick = (event) =>{
        sendValue(Math.random()*1000)
      } 
    } 
    window.rendered = true 
}


Streamlit.events.addEventListener(Streamlit.RENDER_EVENT, onRender)

Streamlit.setComponentReady()

Streamlit.setFrameHeight(50)
