import{a as u,u as _}from"./links.6fea55de.js";import{B as m}from"./Editor.4280cb48.js";import{C as h}from"./Caret.660dc2fe.js";import{C as f}from"./Card.79833296.js";import{C as g}from"./SettingsRow.aef25413.js";import{y as t,c as y,D as s,m as r,o as a,a as w,l as v,E,t as b,d as x}from"./vue.esm-bundler.f425fb9b.js";import{_ as C}from"./_plugin-vue_export-helper.c114f5e4.js";import"./default-i18n.3881921e.js";import"./isArrayLikeObject.a77a8422.js";import"./tags.37883cf5.js";import"./index.c4983756.js";import"./Tooltip.7040733e.js";import"./Slide.ab12a8fa.js";import"./Row.c43f487a.js";const S={setup(){return{optionsStore:u(),rootStore:_()}},components:{BaseEditor:m,CoreAlert:h,CoreCard:f,CoreSettingsRow:g},data(){return{strings:{htaccessEditor:this.$t.__(".htaccess Editor",this.$td),editHtaccess:this.$t.__("Edit .htaccess",this.$td),description:this.$t.sprintf(this.$t.__("This allows you to edit the .htaccess file for your site. All WordPress sites on an Apache server have a .htaccess file and we have provided you with a convenient way of editing it. Care should always be taken when editing important files from within WordPress as an incorrect change could cause WordPress to become inaccessible. %1$sBe sure to make a backup before making changes and ensure that you have FTP access to your web server and know how to access and edit files via FTP.%2$s",this.$td),"<strong>","</strong>")}}}},k={class:"aioseo-tools-htaccess-editor"},B=["innerHTML"];function H(V,n,A,e,o,P){const i=t("core-alert"),c=t("base-editor"),d=t("core-settings-row"),l=t("core-card");return a(),y("div",k,[s(l,{slug:"htaccessEditor","header-text":o.strings.htaccessEditor},{default:r(()=>[w("div",{class:"aioseo-settings-row aioseo-section-description",innerHTML:o.strings.description},null,8,B),s(d,{name:o.strings.editHtaccess,align:""},{content:r(()=>[e.optionsStore.htaccessError?(a(),v(i,{key:0,type:"red"},{default:r(()=>[E(b(e.optionsStore.htaccessError),1)]),_:1})):x("",!0),s(c,{class:"htaccess-editor",disabled:!e.rootStore.aioseo.user.unfilteredHtml,modelValue:e.rootStore.aioseo.data.htaccess,"onUpdate:modelValue":n[0]||(n[0]=p=>e.rootStore.aioseo.data.htaccess=p),"line-numbers":"",monospace:"","preserve-whitespace":""},null,8,["disabled","modelValue"])]),_:1},8,["name"])]),_:1},8,["header-text"])])}const G=C(S,[["render",H]]);export{G as default};
