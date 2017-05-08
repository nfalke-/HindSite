// Get the modal
var modal = document.getElementById('modal');
var modalImg = document.getElementById("modal-img");
// Get the image and insert it inside the modal - use its "alt" text as a caption
var imgs = document.getElementsByClassName('screenshot');

for (var i=0; i<imgs.length; i++) {
    imgs[i].onclick = function(){
        modal.style.display = "block";
        modalImg.src = this.src;
    }
}

modalImg.onclick = function() { 
    modal.style.display = "none";
}

var vid = document.getElementById('vid');
var modalvid = document.getElementById('video-modal');
vid.onclick = function() {
    modalvid.style.display = "block";
}

var close = document.getElementsByClassName("close")[0];

close.onclick = function() { 
    modalvid.style.display = "none";
}
