import{f as i}from"./links.3e8e8c78.js";import{a as n}from"./addons.de5dcd6e.js";import{l as u}from"./license.23316df2.js";import{C as l}from"./index.3770af44.js";import{r as c,o as d,b as p,w as h,D as _,t as s,a as f,f as g}from"./vue.runtime.esm-bundler.c7867100.js";import{_ as m}from"./_plugin-vue_export-helper.8da217d5.js";const q={setup(){return{licenseStore:i()}},components:{CoreAlert:l},props:{addon:String,coreFeature:{type:Array,default(){return[]}},addonFeature:{type:Array,default(){return[]}}},data(){return{strings:{thisFeatureRequires:this.$t.__("This feature requires one of the following plans:",this.$td),thisFeatureRequiresSingular:this.$t.__("This feature requires the following plan:",this.$td)}}},computed:{requiredPlansString(){return 1<this.requiredPlans.length?this.strings.thisFeatureRequires:this.strings.thisFeatureRequiresSingular},getRequiredPlans(){return this.requiredPlans.join(", ")},showAlert(){return n.requiresUpgrade(this.addon)&&this.requiredPlans.length},requiredPlans(){if(this.coreFeature.length||this.addonFeature.length){const r=this.coreFeature[0]||this.addonFeature[0],t=this.coreFeature.length?typeof this.coreFeature[1]<"u"?this.coreFeature[1]:"":typeof this.addonFeature[1]<"u"?this.addonFeature[1]:"";return u.getPlansForFeature(r,t)}return n.currentPlans(this.addon)||[]}}};function y(r,t,F,a,P,e){const o=c("core-alert");return a.licenseStore.isUnlicensed||e.showAlert?(d(),p(o,{key:0,class:"aioseo-required-plans",type:"blue"},{default:h(()=>[_(s(e.requiredPlansString)+" ",1),f("strong",null,s(e.getRequiredPlans),1)]),_:1})):g("",!0)}const $=m(q,[["render",y]]);export{$ as R};