(window.webpackJsonp=window.webpackJsonp||[]).push([[167],{394:function(t,i,e){"use strict";e.r(i);var n=e(3),r=e(2),s=e(35),o=e(81),a=e(44),h=e(54),l=e(7),g=e(45),u=e(11),d=e(19),_=e(91),p=e(186),c=0,m=1;function f(t){if(t.frameState){this.sliderInitialized_||this.initSlider_();var i=t.frameState.viewState.resolution;i!==this.currentResolution_&&(this.currentResolution_=i,this.setThumbPosition_(i))}}var v=function(n){function t(t){var i=t||{};n.call(this,{element:document.createElement("div"),render:i.render||f}),this.dragListenerKeys_=[],this.currentResolution_=void 0,this.direction_=c,this.dragging_,this.heightLimit_=0,this.widthLimit_=0,this.previousX_,this.previousY_,this.thumbSize_=null,this.sliderInitialized_=!1,this.duration_=void 0!==i.duration?i.duration:200;var e=void 0!==i.className?i.className:"ol-zoomslider",s=document.createElement("button");s.setAttribute("type","button"),s.className=e+"-thumb "+a.e;var o=this.element;o.className=e+" "+a.e+" "+a.b,o.appendChild(s),this.dragger_=new p.a(o),Object(l.a)(this.dragger_,_.a.POINTERDOWN,this.handleDraggerStart_,this),Object(l.a)(this.dragger_,_.a.POINTERMOVE,this.handleDraggerDrag_,this),Object(l.a)(this.dragger_,_.a.POINTERUP,this.handleDraggerEnd_,this),Object(l.a)(o,u.a.CLICK,this.handleContainerClick_,this),Object(l.a)(s,u.a.CLICK,g.b)}return n&&(t.__proto__=n),((t.prototype=Object.create(n&&n.prototype)).constructor=t).prototype.disposeInternal=function(){this.dragger_.dispose(),n.prototype.disposeInternal.call(this)},t.prototype.setMap=function(t){n.prototype.setMap.call(this,t),t&&t.render()},t.prototype.initSlider_=function(){var t=this.element,i=t.offsetWidth,e=t.offsetHeight,s=t.firstElementChild,o=getComputedStyle(s),n=s.offsetWidth+parseFloat(o.marginRight)+parseFloat(o.marginLeft),r=s.offsetHeight+parseFloat(o.marginTop)+parseFloat(o.marginBottom);this.thumbSize_=[n,r],e<i?(this.direction_=m,this.widthLimit_=i-n):(this.direction_=c,this.heightLimit_=e-r),this.sliderInitialized_=!0},t.prototype.handleContainerClick_=function(t){var i=this.getMap().getView(),e=this.getRelativePosition_(t.offsetX-this.thumbSize_[0]/2,t.offsetY-this.thumbSize_[1]/2),s=this.getResolutionForPosition_(e);i.animate({resolution:i.constrainResolution(s),duration:this.duration_,easing:h.b})},t.prototype.handleDraggerStart_=function(t){if(!this.dragging_&&t.originalEvent.target===this.element.firstElementChild&&(this.getMap().getView().setHint(s.a.INTERACTING,1),this.previousX_=t.clientX,this.previousY_=t.clientY,this.dragging_=!0,0===this.dragListenerKeys_.length)){var i=this.handleDraggerDrag_,e=this.handleDraggerEnd_;this.dragListenerKeys_.push(Object(l.a)(document,u.a.MOUSEMOVE,i,this),Object(l.a)(document,_.a.POINTERMOVE,i,this),Object(l.a)(document,u.a.MOUSEUP,e,this),Object(l.a)(document,_.a.POINTERUP,e,this))}},t.prototype.handleDraggerDrag_=function(t){if(this.dragging_){var i=this.element.firstElementChild,e=t.clientX-this.previousX_+parseFloat(i.style.left),s=t.clientY-this.previousY_+parseFloat(i.style.top),o=this.getRelativePosition_(e,s);this.currentResolution_=this.getResolutionForPosition_(o),this.getMap().getView().setResolution(this.currentResolution_),this.setThumbPosition_(this.currentResolution_),this.previousX_=t.clientX,this.previousY_=t.clientY}},t.prototype.handleDraggerEnd_=function(t){if(this.dragging_){var i=this.getMap().getView();i.setHint(s.a.INTERACTING,-1),i.animate({resolution:i.constrainResolution(this.currentResolution_),duration:this.duration_,easing:h.b}),this.dragging_=!1,this.previousX_=void 0,this.previousY_=void 0,this.dragListenerKeys_.forEach(l.e),this.dragListenerKeys_.length=0}},t.prototype.setThumbPosition_=function(t){var i=this.getPositionForResolution_(t),e=this.element.firstElementChild;this.direction_==m?e.style.left=this.widthLimit_*i+"px":e.style.top=this.heightLimit_*i+"px"},t.prototype.getRelativePosition_=function(t,i){var e;return e=this.direction_===m?t/this.widthLimit_:i/this.heightLimit_,Object(d.a)(e,0,1)},t.prototype.getResolutionForPosition_=function(t){return this.getMap().getView().getResolutionForValueFunction()(1-t)},t.prototype.getPositionForResolution_=function(t){return 1-this.getMap().getView().getValueForResolutionFunction()(t)},t}(o.a),b=e(6),R=e(12);function y(t){var i=new R.b,e=new b.a({source:i}),s=new n.a({layers:[e],target:t,view:new r.a({center:[0,0],zoom:2})}),o=new v;return s.addControl(o),s}y("map1"),y("map2"),y("map3")}},[[394,0]]]);
//# sourceMappingURL=zoomslider.js.map