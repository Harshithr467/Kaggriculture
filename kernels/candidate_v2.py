# Kaggriculture submission, frozen 2026-09-06.
# Based on "Farming Score V3: Replay Revised" by Arlene (lynnsakurai).
# Source: https://www.kaggle.com/code/lynnsakurai/farming-score-v3-replay-revised
# Public source license: Apache-2.0; original route and cash guard retained below.
# Modifications: earlier premium sales with quantity accounting, late seed
# budgeting, early feed reserve, and final-turn cargo return / liquidation.
# The following Apache License applies to the public source and this overlay.
#
# 
#                                  Apache License
#                            Version 2.0, January 2004
#                         http://www.apache.org/licenses/
# 
#    TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION
# 
#    1. Definitions.
# 
#       "License" shall mean the terms and conditions for use, reproduction,
#       and distribution as defined by Sections 1 through 9 of this document.
# 
#       "Licensor" shall mean the copyright owner or entity authorized by
#       the copyright owner that is granting the License.
# 
#       "Legal Entity" shall mean the union of the acting entity and all
#       other entities that control, are controlled by, or are under common
#       control with that entity. For the purposes of this definition,
#       "control" means (i) the power, direct or indirect, to cause the
#       direction or management of such entity, whether by contract or
#       otherwise, or (ii) ownership of fifty percent (50%) or more of the
#       outstanding shares, or (iii) beneficial ownership of such entity.
# 
#       "You" (or "Your") shall mean an individual or Legal Entity
#       exercising permissions granted by this License.
# 
#       "Source" form shall mean the preferred form for making modifications,
#       including but not limited to software source code, documentation
#       source, and configuration files.
# 
#       "Object" form shall mean any form resulting from mechanical
#       transformation or translation of a Source form, including but
#       not limited to compiled object code, generated documentation,
#       and conversions to other media types.
# 
#       "Work" shall mean the work of authorship, whether in Source or
#       Object form, made available under the License, as indicated by a
#       copyright notice that is included in or attached to the work
#       (an example is provided in the Appendix below).
# 
#       "Derivative Works" shall mean any work, whether in Source or Object
#       form, that is based on (or derived from) the Work and for which the
#       editorial revisions, annotations, elaborations, or other modifications
#       represent, as a whole, an original work of authorship. For the purposes
#       of this License, Derivative Works shall not include works that remain
#       separable from, or merely link (or bind by name) to the interfaces of,
#       the Work and Derivative Works thereof.
# 
#       "Contribution" shall mean any work of authorship, including
#       the original version of the Work and any modifications or additions
#       to that Work or Derivative Works thereof, that is intentionally
#       submitted to Licensor for inclusion in the Work by the copyright owner
#       or by an individual or Legal Entity authorized to submit on behalf of
#       the copyright owner. For the purposes of this definition, "submitted"
#       means any form of electronic, verbal, or written communication sent
#       to the Licensor or its representatives, including but not limited to
#       communication on electronic mailing lists, source code control systems,
#       and issue tracking systems that are managed by, or on behalf of, the
#       Licensor for the purpose of discussing and improving the Work, but
#       excluding communication that is conspicuously marked or otherwise
#       designated in writing by the copyright owner as "Not a Contribution."
# 
#       "Contributor" shall mean Licensor and any individual or Legal Entity
#       on behalf of whom a Contribution has been received by Licensor and
#       subsequently incorporated within the Work.
# 
#    2. Grant of Copyright License. Subject to the terms and conditions of
#       this License, each Contributor hereby grants to You a perpetual,
#       worldwide, non-exclusive, no-charge, royalty-free, irrevocable
#       copyright license to reproduce, prepare Derivative Works of,
#       publicly display, publicly perform, sublicense, and distribute the
#       Work and such Derivative Works in Source or Object form.
# 
#    3. Grant of Patent License. Subject to the terms and conditions of
#       this License, each Contributor hereby grants to You a perpetual,
#       worldwide, non-exclusive, no-charge, royalty-free, irrevocable
#       (except as stated in this section) patent license to make, have made,
#       use, offer to sell, sell, import, and otherwise transfer the Work,
#       where such license applies only to those patent claims licensable
#       by such Contributor that are necessarily infringed by their
#       Contribution(s) alone or by combination of their Contribution(s)
#       with the Work to which such Contribution(s) was submitted. If You
#       institute patent litigation against any entity (including a
#       cross-claim or counterclaim in a lawsuit) alleging that the Work
#       or a Contribution incorporated within the Work constitutes direct
#       or contributory patent infringement, then any patent licenses
#       granted to You under this License for that Work shall terminate
#       as of the date such litigation is filed.
# 
#    4. Redistribution. You may reproduce and distribute copies of the
#       Work or Derivative Works thereof in any medium, with or without
#       modifications, and in Source or Object form, provided that You
#       meet the following conditions:
# 
#       (a) You must give any other recipients of the Work or
#           Derivative Works a copy of this License; and
# 
#       (b) You must cause any modified files to carry prominent notices
#           stating that You changed the files; and
# 
#       (c) You must retain, in the Source form of any Derivative Works
#           that You distribute, all copyright, patent, trademark, and
#           attribution notices from the Source form of the Work,
#           excluding those notices that do not pertain to any part of
#           the Derivative Works; and
# 
#       (d) If the Work includes a "NOTICE" text file as part of its
#           distribution, then any Derivative Works that You distribute must
#           include a readable copy of the attribution notices contained
#           within such NOTICE file, excluding those notices that do not
#           pertain to any part of the Derivative Works, in at least one
#           of the following places: within a NOTICE text file distributed
#           as part of the Derivative Works; within the Source form or
#           documentation, if provided along with the Derivative Works; or,
#           within a display generated by the Derivative Works, if and
#           wherever such third-party notices normally appear. The contents
#           of the NOTICE file are for informational purposes only and
#           do not modify the License. You may add Your own attribution
#           notices within Derivative Works that You distribute, alongside
#           or as an addendum to the NOTICE text from the Work, provided
#           that such additional attribution notices cannot be construed
#           as modifying the License.
# 
#       You may add Your own copyright statement to Your modifications and
#       may provide additional or different license terms and conditions
#       for use, reproduction, or distribution of Your modifications, or
#       for any such Derivative Works as a whole, provided Your use,
#       reproduction, and distribution of the Work otherwise complies with
#       the conditions stated in this License.
# 
#    5. Submission of Contributions. Unless You explicitly state otherwise,
#       any Contribution intentionally submitted for inclusion in the Work
#       by You to the Licensor shall be under the terms and conditions of
#       this License, without any additional terms or conditions.
#       Notwithstanding the above, nothing herein shall supersede or modify
#       the terms of any separate license agreement you may have executed
#       with Licensor regarding such Contributions.
# 
#    6. Trademarks. This License does not grant permission to use the trade
#       names, trademarks, service marks, or product names of the Licensor,
#       except as required for reasonable and customary use in describing the
#       origin of the Work and reproducing the content of the NOTICE file.
# 
#    7. Disclaimer of Warranty. Unless required by applicable law or
#       agreed to in writing, Licensor provides the Work (and each
#       Contributor provides its Contributions) on an "AS IS" BASIS,
#       WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
#       implied, including, without limitation, any warranties or conditions
#       of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
#       PARTICULAR PURPOSE. You are solely responsible for determining the
#       appropriateness of using or redistributing the Work and assume any
#       risks associated with Your exercise of permissions under this License.
# 
#    8. Limitation of Liability. In no event and under no legal theory,
#       whether in tort (including negligence), contract, or otherwise,
#       unless required by applicable law (such as deliberate and grossly
#       negligent acts) or agreed to in writing, shall any Contributor be
#       liable to You for damages, including any direct, indirect, special,
#       incidental, or consequential damages of any character arising as a
#       result of this License or out of the use or inability to use the
#       Work (including but not limited to damages for loss of goodwill,
#       work stoppage, computer failure or malfunction, or any and all
#       other commercial damages or losses), even if such Contributor
#       has been advised of the possibility of such damages.
# 
#    9. Accepting Warranty or Additional Liability. While redistributing
#       the Work or Derivative Works thereof, You may choose to offer,
#       and charge a fee for, acceptance of support, warranty, indemnity,
#       or other liability obligations and/or rights consistent with this
#       License. However, in accepting such obligations, You may act only
#       on Your own behalf and on Your sole responsibility, not on behalf
#       of any other Contributor, and only if You agree to indemnify,
#       defend, and hold each Contributor harmless for any liability
#       incurred by, or claims asserted against, such Contributor by reason
#       of your accepting any such warranty or additional liability.
# 
#    END OF TERMS AND CONDITIONS
# 
#    APPENDIX: How to apply the Apache License to your work.
# 
#       To apply the Apache License to your work, attach the following
#       boilerplate notice, with the fields enclosed by brackets "[]"
#       replaced with your own identifying information. (Don't include
#       the brackets!)  The text should be enclosed in the appropriate
#       comment syntax for the file format. We also recommend that a
#       file or class name and description of purpose be included on the
#       same "printed page" as the copyright notice for easier
#       identification within third-party archives.
# 
#    Copyright [yyyy] [name of copyright owner]
# 
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
# 
#        http://www.apache.org/licenses/LICENSE-2.0
# 
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

"""Pure-Python standard submission for the three-day shop router."""

from __future__ import annotations

import base64
import copy
import json
import math
import zlib


_ROUTES = json.loads(zlib.decompress(base64.b85decode(b'c-rNCO^+POa^!#Exerqx{k1o~VM#-XGbBjP7PJqIhX+WD1qA8vq}yWu`;zRgs?2nAGjoqDawMJDXjW%MMtDTHo12^e`Op9N)&KtM-~RQV|Mu#C{Q1>~*PlMUdb)Y_fByP!|Mc%)e(~kUfBoy<{^g(l<IB%~e)Xr{|M4#$KE8kR`_G?W-Ml*fa(Mma-_7pn>HpnKAM)G#kDq_ZpYrMO?%n0jAD(WWAN=WXcysyn{o>cZ9^SqG?aP;KzyAK0w;vC$+#kL^<n?cFe|`P+OMiZUe08%8zy9>g;qc+>e=OeQc=+^r`XXN@=<Uz{@cW0CCw+a+%SSG6J^9uA!)z8d`kOD$KR@<)*z+&H{Pd^a-@beEmoF>&`S-6=;Vk8H6d&Hb{_XR5_GiOcJbgN>=cmmF1IGO2;Xfa|$+>X{e0=@+@NuzX)33n`21fq#>o{lqQH8~Pe*6ub#>JdZM*RH4N`oS6dokdbxw|adX@aA@UvC93-}HB14};m1#Q9rwG>6yW00_%-UQ04<i@&<s=<?;6&EE5;RvN|2`y=}SgILVgTE@J%x6nFG_WR5KUAFsl>9U2AoBA^OU=O2(iOZlD_<R<C2Zo=>qeo{fetPklD@<MZX>{sdJ~UnbZ`0D6x69m|ADd6x<TvUY$7kz#Jhhj4{tcY0^Z#`wYyP)nM%H@%WU|&Bck%;!?9$IjJY?zCY703m4LdredY=YI9=b~4wAaVa%Uv{i^7(c`=h^drlIO)sh`3mn=SDYg`P}#K-W`7a{FlEweEj_O-P`}Q^iAOZQ~w10Md=(nc^BDNp6&6|``?$VaK2(Ee@yP#5Zb*wQe5_@PvNl+jAsv=*f<x)@|@3v%TS3w;tg)AoszRn7Gn?j;LAmJIsON(v^O8$f0&>7=iNDSc23@UjiY$wlRa*rKhWU**i*NzYw+J`a2+pV-KWjZpD#zO!0p0e=z?%_fbaH6dIZFYiHEfxlzRTkG8he~yYdV`>|1e=fbT`0s3W2{!6b6D#uz6#jHej2sYwOV2*aVIpN#I!!f=Vrg2fs#S~NcSJT;qau=3@BFF5h0q95|h>yQ6ajW|x|d4<4I`G`ZDSv1u12v@Py%QwvY;YF~kcNs(ZdS(l}=GnOq4dOiia2?_Gu*dnAh~CYUDtsKB<p+l;+FAbEqX#nRRU<I7ECnAY3-F}f6JNnFoU6JXyFMUN^fgL=iGO}OE{t_AXy>Ek-V|;i+o?f6Ex&qv1NHn8?^*^&XUFB?!=7F##?$R91&to0H99akz7FFt<lN`%;7y0iG7q&?2a`mmu(a&R|AaGV9MWRdf#<_Kik9cb+^q1mqmKrtM$c*4C5Kb|CgwFm-(_d|E)pO<L4KDd%T1^D`qJA(wjMo^B(nDbcIfEN(U)S9Vd3E10N#!N1!{%PPdcNX7L?xbv^vi<Q)n}a%i@g+F4*mm3x+(e`LDms(#Q8GvGD!TpKCZpsqa<aZ(v)1>;eCt$;5y9{PFeiPlt~m{}FswoczniGd-||#|mDj<cYbrCb$;#(;5E`PX7@6hVEL&y&{teT#y=K;$lb90pUrvn)3ks&ZXUSh>gtR&sGwy&tZV+^1B2?F&S5`&oL#Upqw!=2k(?3fpqGFt+QUpM_A>y_MW%aQjNU^AP11=4a`6JqO;dj0Dgcgf7^$ZIQ9r$?k2q&cTe9H@w#0z*%rO8eINIt&Y#|#F{!w=LkH+W-n%UQlpEhqvd`T?a18Lp@s&FGJyn;a@aW=#t?2h5w=&#Gove%G60Jp4#poeG5-W*?Y`QMQo)=$WvIEGk=^Jw5l(W-V^h1DK=O{ss#w&}0phEW5Oge#g&=)^=HgI4;KGQK7P=c{69mox%mO~|#G01<;jPX!^Be|PfYaTZ<16G%$u5PkD_w_7(d0sOW94hopInR(gX5bvy7TmAscNX6HN(AqvIS*tp9sh2dplhQ?EhBk@b&pPM_*l`ob;o`=Y>4x@6XORI`F!wtTgDo-_?7ZA<SXGjgBrB(rHFiNf2-{dfrn4%_SL^J9Gm0&_g{=@^OM7oM{l0eKg4h@k;HibWx_Z+319y2%Z>L&)iGb5Ou-uFX~t_RQopm$bU5>LpgA8Xjs?6zguhl8a7yw|YkD9Kw@hPQ2CcRRd55-#8^;BT*uYe?_``*imX$HkEMxgh{0+!2XDqwY!IB%_jGZvcyuosASgn(@M%Jv?i4p$UCKF#e?l4tvl$WqiAH7P(S^4aw=8IN;+Q8_xgQ$TJpvFa)--%+SNTGpIlVA{y6!luw`iwPMfl*M17ZC$?s2yXvOoz%YQWw%?O_)VL!C0v{RlqXSI^q;q=!E;r`a6rfW8Ua5d-l;NVob<I&a|gorq)uyqjBrVoSepi*9Od`y@=j%?G`uByyoqi;V?rMDyb0U=NNU*D%dy3WJeXuCPSeCd+p;RBxfMhk{5HYpZ__Z_vimR|BxmH)<`s5z6GEC=MP?fP|p5(@%Yr=LvCF5XZY7Lt~TMG@z7NTPI;t7iI~0*Ud*#3Ge>DB$=?hNd)GdQSatuIcPJu-oLjsG^CU)P*;ZiS!B`CgOGdMA<?dh2mqQW&>1N>hjxnCx@nB4I^5z}N8l4M^zSmCTdbIb&cJXG)SOfOn5fv*qs-0RpQe^8JKCn*~t@jLpeF>VRhKv#mGeN*ZaH~d2i&8l9i4~bN^E%9@!l1mZCU^k?po>Fv{!QxZTveDV{r~_A|0_M!)s}igGv?~0>uym_aqq+V#rL2CX6Zc|;*hH85|n?sGJbvg?jK&=+~N3x($4UiJAWv@ZO*py{P~3hZ-PS`nXRP@>WcC*#S-T80H_IoHyR-{VB(#TWCuX|TqE~+rf5Eure+$EJg_A272^YOr_D|QEL|&a)WiBGc41J6!jYmb!aF$~$<AB!3=$TTq><7MuO03gVk2On#WbZ@Yjrc_%gJClGg4f)atab44^E-5C#vDjFF}815z2CB9V&S@U#r6rsR6EB27B6~t$lOM3xV;y$kcm^JaA!a9xEKA=G1xMFDG#FSmuxc>om@?O3<@BGdLnW3>oeNY7cAcRUIs-iBH(D7*m?yOUZDFqAA=EWy#f&uqyQsRPuo)_Y2BDQZh;=zDd~6N#EtlucB>S>i*e87nG&PslwId=FKp>7*=*^Zt(LaGV8rys9&nu;*{ZK=(riqG7-jZ{4e5W42ugJK2c0|#&KNYkl2r<QI-d?kRrtih9szowg5qQ-nyyI_D^**)ne|_R69?4RI1S{mI%s*te7|_Wff_!1R|TT21VxFR%aLpzH4cCny>)BsxaC>?t~FzP<%rJ!Z~mMfpO{|G{6{-d<S#B%!g;8EP?4@xHG?t9@&_b)ha#h2at?QX(vlaML|pjU4zq(WH+ddlF<yz97j_kbr~>13Vu2?_gKmSt=%^=zix;ae;SgB&4B72Q)#(+B*vDoZv39XwFm~3#RtBPl*RaA3nMzjP)|)9os`a4C<o{zR*B&o+L_MW<P<A`=J1h+V3L($yaZ9TiG%~ceJa#}ccS4n)7eRYyh;$fN}DAu!z*)Sf<ipa66Qhfu0?#Vy~et6{Vw(TZU;%+?oTn;uQVAbI?(P<h#Z3EeLxirIuAS<=~C#D3t)P~FJsjb?vN>^pfP8kWeO`ocg{~(0SP!7s_{zPw$z?ALh4F`k1>L+BWK8*3n6d9<!=SV^U_@U4$Lto!c0Doch;UC%C{MN{PJYToCD*v2;|d0K)=iCfEWHa%Wk|pZoBtSZ-g#`!J)muUy)$63U)MJakH(!<OtN_>qvZwSaL!|gM5R%?NIe(hi^+o)&St98ddX&<8Rw)UI<<iy$9<mDG#0$hBt0)Z>bg~w?DrR($;jR5p`EocqK}3Se;{Mu^79{X}Jqx;#62-wG|=41zeWIhicN}!Dg6#C3k}3__C$XV+K|Kj9`Zf62wcmR8%LFjeP7}=U~#cJvS;$Ewitg#q5=s<cwM*%6x%VGlL!H6H+7I2P`P^?yc!fCNQR$VvFD<46}P`^zwGV3<iCG;?H_}*ABLVM^mfz93wFVw<!@w+TqfI&88u5_P8>_!#!gM3Ryz~E*FAoG97rDK#@(Qpa=zq5Qi`Nj>Ae#6&5K+G0sN}$RpWPAv0Vo$4}TN-~dO7Yhyg_JhGY;oZaVqZIM)2{GH;Jn9Ug$p2VGjEc)5lWay;AHY<Hg{I6DO(&}gdGDr>c&r!=}DY3oZl-W^I2UqmyPBVx$q^W47E3pkyL7ygaEhUmESzBsR<@M+*@oPZ*ArB_jWDVqXTW!6VNHp&t0!9#te{LPh>a$FU`XKmF<0XGOIN9V(D?}r#aGSRt964!NmAh5Jz-m)Wc1@d#qNQMkK4E_3BLge7Rbovs)6SH5Csw;7(W<LnK8JDxG%+KdMlPA7*y)Lg^hGAbQTDci`6y@gsXSh)-7ZXn-4_Mja?dis*w}5M_T*w2N?LoYyCa=U03em`hGnHmQ3T(?d5ZNRg{3YNU><(}0mc$<xGjJKq=v$+t=jBs84^~4Xw`N!lI?={dq@-NjUo+J-zaZ++Z}M0iz>M9i|X>rKelN$ydrr)K(9!CF>!KQh*6;DLsO2{wA@=;No<F;j-7klwygs5m{0)9of4E`(Unr19lwwgp=a^fp}8I-(;0t5X#y@57RP7syEybR)??f@I@=$o^)#+(p(EU@Moc;Tgn3@*T6A;@Wa3@476!t2#`eO3qDQOp-fu`nlVm-V03Ro<wpj|F!}`#U1bk)o2!aTx<JsYaXSD!5Fm;=lhh}+nga)=08ErEHc^t|LF|M3QArNCI*mRz2ZYZ<Ik+QOg7$WK%{c36VmCGH*I>X-M4Eo~_4g?1)1?uVaMoS8dcS+(weHfSxyTFx8^+!^&^}0<>!Er?8TTHLNnFvP^x^&=N8tT}+lBW?RoiBIsn&s{c;m2BT1Ql!|{k}dC0n0Is&8&*=mJXsJ+Az7%d#W2*GgC|P7geIajsz(#xdF_9k}!28NUi945HFl@X9|FY4q{zRJ1<&QB~LlSxTJH3pi*#CFvs3-wo8g*EYV4eucQ4HrbhM#@%y#ML)%Bl3Nsh&jVosMx}6{DiUq{V2)Yb!F(xr4&pBdRRPBUaS~2~0eH)`fCWr=;6SR%$0TQqw=R*1fc7~cw<WQVR4^0-1#veNKC&Y7l;inP&o&v2*;P1z0AA!RQv8<G`eXAP(`SsKw2!AB9=o}M{!E_X8r(px-F^dXk>SNt>d+`Y3H#nKHVS-A}Z-d({{xc-J$cybNKtU-2Va|6fy<6(<k0oV@>>n=d%V#sfB&50~nbY&s)cRv$Lf$0RdzS>bfJ_()Z5HX>J0m^A`d&>2L?-{}8V&mY%IJ&eM8Sp+BZ_jFA)uX46~_@44_+{uYC8$X0vS+~!9<scRTl6s6PLpx6QlN5Ft>sT18Z>$l&w}YJk=<`tBNRfOS3JH$*oIj1l(FfswFJQ0pXe-Po{9$FbYefAI#`53ED+7Yhl)GFXXV=DyEmp{3*TmG|FsJ517KbXy4|;WWA2&q)wQcq6HXhFvn|l9wU2NkDsGuqusS_Y50OgGU3c2wr{i6+8p|tDd36go>fnO=j3nDB^3O^L$Pa=D3Qhi_r6jI8Nq|7?U)9gx3yntZ9NG(+_&D1wSI}h3bSLF^GX}^D%z=z(a?yTX{q@X^d>Ghy0T%#>#^y5g;^9jeN%*J`XUAQgUR2G&aRDC0i??p9~w<xXH!R9Vq&9g6DCsf^J_L1HLy}3ibFLm7V6w&v(dDOX;3kn{)1aJXy`WfZGv~oinAZhRz}045!-y;-n{+${A48NN?{ngW&5U7F^u-p^j%1uSKp8cNvK`f+7d!FI?)#gsceIJAK>1N8hp<ZT(_*d!?O;iA>?&C70o{VY3IOWyD-}MQA0g7iVpQ{BjKso^@F@*hw+qMaTPiM18&n|-ELtpm{W+8Q7Wa^nzF(d^9nQKP68JblOQ%YT2m#ghh(&vDumnv)ym1M86daCe7F@$a7!sVdS{A|(1Lj_a+d`?7^L*Vt?=X1`V97vn%ri|Cy&V&a{1$k!=|Eid;xJxay*47(&t2%J!QTtunGBkKRp$MZO9LCWk~^A>nLXfi#feiSKhtLjb_T_NdJ&WHjLg<a6NPAx+YFh|7yJ9X?ZT1*=BXH+l+x#cu!P#v41sI=?4;Tex<U1rvqoR<72WYTqXVs!G6+se$21)oA1rTY78Du{683mb@D)-w`>-zi@Nh>?IG|?_vsB!@@v^a91YCwJnCF~q0O$-a5x@>mNXSjZI-|cqB&M#V#}`=ZB4)%rQr0TUbjyAkJGjojLyNkSo$Z6VsA74!~#TlNOv<yh9tZO0yLk#tUyO%4PTh<U$fb1G0t4kyhYKxXb<lyjLsqd!0(IZ&iT(#$bE8{J<D-N&zDv4psi$v_pxb;+8_i$Il<auRbo2?uEnTf7Q)siMT}5UR4KBP+W(=NcAv0-E!bv0fbNAObrFn%F$<+1%hU~TW*3q0<5Qcy@yC#EqkY3;NyMTq#4hgF;Q!7Lzi%@;cri$mmf=xXdVGjT44`2i)2x%kjRG!j$yzhssmO%HOKYt2yX-P!H;*nftYYMFTfOk7r!L#Wk*xChER|wr3sZ}J?mPkzHRJ}9y%OvQ_=kAbZWe+R_A-aOkoD~6y+>-zLHSaVI+~O;QE^3T=4L1fPo5H;Nmvade6YdT^4nQqL~U>K5E9x6KPn8tleLAy70Q#raB}xht%{y{xR)GP<tRjojBVuV#6vtTsm1$pS*5MR?4kv`nEUjVh506wkGX*`B^>mA^U8>JtKyn*Q`3~xvg*Va8ZvryuL3Nja^PA_uGB#iRhb$hdm2?Q#JFsHM6Hm>-_<lJ#+KaHGi0J1tY{?)Ru<C?Uk@jID3qlPeOU@B5Ro6u7&H6HYFHRv{BDItfkl=H9RJ;aE{G)J!wdk(ff1`lLWJkHt}eqw{`~sIF%<Alk(Rv%iAaAtXZO><!Ml<eutO_3mpq<+@W28Dsug&-ETjl<!Wimg_E~~S=BpTmrNeGjbbTtns6q|D8ST`qh~8yIJ%hWA(2q&t9fyaU_TI6(H{2<<BU%hm<gV<RpT%35X2U8P=FIa7d{n2Tv=RYXXjmm8C#DF|!-A;lSW!a8>tHUdbmbU5t3Tz@L9p}@U=o=U$SPD1J?A2A%(VLfDo>P6Kv8_UF~<oM6jaG=-EM8elg3_oZuH=f6mQ|jrQ@|QUFpFFiAQ2GM*=Ks1sICi^`T9k@?ia+VA3Id#~SB^;|E#YBRHWgQ3tEI)L@!e`o_^KUdH2IqZqLvvG(V1aP1#B)QJR+45Ne)-pGpes-P4iJCaK$qIA*HnJVR)p*ii<=}2;TEOp_@P%nleHxR?aplDII12heF$_*y}K=nZjaS@6`H%fmhnxH0JGtmcJ2b>u#s$s$!1cPba#7C=&qolV&vN>a8<!NSCW+R;&n~mNU8f#Hi=&Kl<rh+goaDti4rqTl8<sZbHY0Ok_FW{BUXVE54!JD;0O$k=s+_}VeSwnfD(^X6bO+5-slF}P;%$VUU@Q$>fDJx;12#08U9<m5s)HjkAGhosw>m)Ex{d7cTj1n{gp7Z5%G$vGRpa;!UVb-XY=-`VZrrL^aY|l3lT{ap086UP*W)edLx~~}b%W-L1CIJR3st8n>81t-%1t?BDRY-yRUAaqsS+jal3B`dngCKBTF+`JGI+xQR!2s)tI_9Csk;DRuo5p0Z$@u3(khBNZ504k|JF;z@8dfV?$@m%4e1WVfNiz5y-A$K(6FKto99z^ipBWzwi8V&4+qUXULS<sojudYiiUbu}w)`R4G|caH^kRAQ7J_1yfSc`A1ZFKJk?{(aPAf?UL71zQDa;!__);9?VD<~86gZz{P`G?)L3Khl_!!|?`wHesh7-q>MJ0p=lH(-|UGRq1c+>!>j45}g_i9PZLvTY_5g+AE$QRk_lmjhh1O7z?p*odd(?$t8&nR{^oZa~_OARqc0W6ltYs!Xdv1Zz;T6DBPA?xIO*2t~L>p<n;<JE<urV&C80_Y>MNi+kHBz(R2igRzWtyi*X<G>eWSfkecMnQ#s@;ozhxYv2)#%~iJ6B3j^fG>lsXtl_pEroQQZ8UhQ8AMxD`K_%1-AA*xsNqYN3#)l!+1|z09?|EiPgzcSL6fQBp78PwQVT2LA+D9wKV<2(G0iE;e6wU~h}f2vJnr<MrgG_~l$!F@nWH&i<_@!_6;jaJ8OfGyP;Q`il}e<NhQ5~M-FQ9alI8SA)QEwlJf=*ouerM|2c^^M<8>5ztzt~tfRb@xb0SU;JBW}qY`Dl8L(*8=A0BB#Yk09TVc#FQQ#S_Zb}hmTFVfFnqJhF##w+Ai(7Be1AG4@)48<s$J8>SZrad`GGDZ)oY=Z)+)47YSs`b^kh5HkeLe*7PqxJL{CdssUMXr;)==h1w)yB<UPd!1Fx-}Q{Ra$(MPJ{;#ELlj1`)DL?I4g?s$|UqjGlgDgyA08j=pcFq@Ec6LwS6BHblYI$k8pL~BT6W<j*CArUXvFCY9)#M((36EA&wJ<APT2Gtw*9z#u{=^D0;Jcv<YPw?$*rQvZ*}yDZL!2EGXW-OL|%7gaRt8?REAtMb9?|FCu1m<A`INM6pnM^_Cbow!kh^rBR1sTq=ifYfP=-@7apH=pd!+qKv4rnsBcpJEI}Hno`hzS`C_9amHoMFbus^()6A5W)_z_*VW;g6E<z85q?v;56P3#<GCWT-=y@Aib-4YLOJ==;~v1R^K6nTNu_pT_s?knW3(49&1F$Xn<oAZ*5gf`Gb2O{I(6KZI;t6Ow_kMo<P!{33e(G6impiCST=R$s;l@Rx3Qv<6o4y>nA;}(QK}hQiYy3(k#3EZ!r27LVI?+&ljNjTn+7{;^W+DPta2pp5~7f2&-AC4aZ$agTdk|Mk9mQXH7Xv$q4ii%zhy!#qEXF>-&fS3RuaC?mey4}V~#8fU*upxL_N$|i2mNuJ4$J~ag=$Jq#bgpdfsb|*3PcMzM;}7eHsosJte~AoT;3ZLv<V|)qsV}r#%Ze4Qo+yz(5G*!@vcmyUgm`zBy_SPX$g667MCd%B<u!eq0_FeFBc(EXu+M?Z0g^a9CBC)7hG?0W6%Vbi%T6pE<{5lXX1apMZ{)F`_al=eDAJ<I!wN!yYP(0$?}QsFm-<3g0tj9O-5n`cC8uWhtW3;TBJuQmWNs85t5W&d8}M4?w<DM%o-IN#;wd*cQw?fs;CX{aAWKT=)u!g%~wh0L%u)=QZt<bZlw)W$!S)0aO8@MPuc!Jf!Nw5OdztxuY0IQ>Kn)m9-@(X%Wv{^mak)74|^G<V7fK_N?~s8fOcvZ}Dy)Gs6_%616&wB>M7pr7WlH7>$#9Oh5t|!+|g}rWc^eCz1w_(otke1d~o7#ue!-Y1yP!4`CaOGRKszk5WL_qp?<Wmy~ro_%)Zku2(21>6m5R$a(ua7+p~EVC{z+!6~_ju&f88k}(p3V4O(>R&pg}orG?9JNY=tMq0)iYVYcyZIu{P&O-|1utjNeL&~N^aj`7{Xg87WSnKzEs@&J)irn5~q~!j)DhA(a421&=rk)JdeH#W{D#V&-J){+HQEO7F4%d9Wm_)4hRK<jq`rs0&x1vl$TICjBG~p32(m+8nSV*UqP>DkLXs(7aeiG}Ny@9EZXSk{*X30eH8vsU+ra&)Kjfwx4;1zR0*$0Q`)FBNedJw?y*d}KZ$g~GB^Is|gcMZ-{pF%LISgGg;Rxe=eH#?jtXtNnG2v4_!MI}(isw(zN2Irx2Gs0d%BtUjViwBgi^Xl4og`)xtQg}>a{7S7@@xqLmghEA`*O<z!N#*e()u=C(His}6TXzMTDzVR^r6e3QW(cR3@Fu<m_(ju3yjwHDz%y(m$(@#c8^^uXJkBR6_r%3VbUkPnBovq%`dLe4t;Bc3^iGhRiV!txXuE>BkhT=8Zr!ttmOzu`py}3aEF};jk3jHrE<wMfON}u?9;{tA>ucDM_Fum;%2ce8U`~@7v&)z<cNp*4-2Y%|jBZuE)iuGWh+qu4F=zxw()d>hB?Fv35gAU=ojMUh0mJbWWDTj<*=!0cS9Jo25M4Ya{XRv^^~ZZj+lD;#hFes*@8pzUvU)Vnmv2sZqIzoA3Uw`<H5@f7B|wVUi)wb^Jq$7l3nQb8F7u72tMbdAetd7WAQ-oJS(X$@9`Q!!G^>tGV8xhQvc{7+CNE}fQ`fv5--z0KUV2h-yID9%8QqFy6e;XzlGn9kw~*46y2z@4R_SZX2`RFij*}m1BE@Ydg!GUt3jM}#vZ)6p+L6(oR7Ce|V!Xb}$vI!!g~VNcS#AhiQ|4ITdq?XOE%;Vx$23)a(`d%cr3LBX%F_iEvu$iIki`N4xM<8c&ui^uaqG*+R@ijlM&Yz2!gp%P+1cBxPFSJaAfJMDnx3o%gscyBgbqd5RE3dHr?08I)7%x3m{(#j*Qy3edVFvy3RG0jIdGx_RImES(;DNF1i&XP)X$7SF5HJJDAg?w__o&r2FX&W8OEHnMf&zFbyUk2l*}}%XnI8S@n-c-*O7Vgbd5MYfl6lQ8KlMw?ZOLX0JYINNq4anfk3Ghb<9@P7%R>0N{WM)QsHd|@zL0F*;`Q<w8F3V32N}askPdh@!29D-S?vc0j3r$_e5Er_iGeDGBYU#*(#sDj2cTpEvxMH)G5{7@1<)qK<0)B1XGi0lJzO)7X_0<X|II)dcrnLH;e**W6D%!S>q80t&c{XNJo*2o;-yz6WN}nNbunQb*-XyfkG;dA>GX_f)mnc$fcdF53w9+50o~MMWF^qt9bm<R-+V(bqYlST~Zo%z1~U#y@eP<y`rTZ57A-NC2w}LLffO+)wa34y525t8pXOE-DQr;;&b<2S%)Jc1>>6`rU^KtASFh2ZiXi7wCq{4^AT}9oD$i>(8k)mRJfsmJe*g8uinw+^xgRwm@D5@&qRc!eX0-L$wG5-Z8T$_MZV8`@tqOhMa!l)t8ABwm{Io4JNH-jB~!N>yzsQ($?Dw3hq5B6z5$$5gOt0c*ip0K?Q9{-jaleb-1T*i#z{Q93%T>{__OtPbY8cttc~Te!p@2%gP39L8*=Z|(~0c|)|s+dRFA8%4pP93ZE6EL3OrI};n<A@J0fhX_M>i9>()hw7*EON0o24?<E9&GE=>uc4D+llJjzTUv#0$6M7Doy?LpB9E4j&Ts8nEeeC7lNI(h=9t;NV59jQR2aR%T5f=o}g4){Zl&6DwM?JX{ru&}de5Z?>KO4xxZQ8L=2k_t3kA4)iR1Ltfc?ZZcY$mrfqIm+WODTC^8I>Tqx8l|Q?FT3y=fk08!?ROo!&U02bQJuv=?<YcuDdN;Q)Tq9X4r}3I4NRBEzZ4ZX!M&`CCEV%q3WmS(`SXSJG#{bfK}M4Isy%*1yNR0W9vwO`Xlk-*qDl58g**+UsLz&U{uRxAwhEf(*V<-VAR<GTi81U`fyOmy|1@c>Qh~A$WT9Ze0R@!>n4?gX1e0{N-L6G8uqT{jgr!1(T14T}+DvX#?v2-LK-J_@wcI&qwb>Tbo{2~z)8E-X6?8>$yO~OY|43ut?>YNw{4jcEjf_cXReuj)^C#OldEWODp&@;5m1co<{O@i4rdSfVh1V02I1cqCan&uLpXG(vZ14jX6o-xuk^#+B*7iu3dbktYR!}Xz*(fREL@2mEltBPpC+{!O4pmH2U@(xOA}@(?gtSnl-!LXt&U$<>df3+S0-bIol2AgXOx0r;Z_-BqOh`mAc3VTEh>1z-%CLH1sg;_{g50ZLgiVo^N@F>=ru2=E#;6oh#xJ;&udy-qE6*4m%j?NLSX*S18O=0tX(OuM(&9Y_eRbI9=;Qkjiux$m*T&_<s+|WTUqw|v8IJG1(1}-6@j1vg9dRkiUmcZ4z^V`rKvWag5caA;3yfZaTY{;VcB!lNhkrbjJc2@-Z_7B7o%AvtJgsq_Gm_g%ba1lnEwq#M-o>e+`$&z1d5zJ`*aoA+ce2J><4CB>B>x{rUuakN{Kxd&9Fqr!)p=N6iVhf1y}#e44=o>^=2@K?_Dc_knzN!lO2S?g(QffUdd7r<a`Sa9zWkcK(fo<?7&6^i!TOl-K9EKxlVAUOc=!Id6Si7zrTY4}x4*vr<_)|*z9heAzy9>g;qbwVgwIs|uTN6P*ZjkD3s)Kvo*(->?97<|^!wX)Z~pRSML+)@jRP+w;9q>p6g<!VY&eUj$107aaqeZzXJk}Q&W$@@)ZS<MHC9(&v7s8H${Dm^8W(f!5j*OGB5NDixR*uCGkw=vLBKCNk1)>Ps-ppNF=2UN6Vt`CE&l3iqw}hV4aKa&D2Q?kle=8knBz?x*2$t$kcHAHY2Y_Z_HawlA1v^pLdmK5E~OcZpY|(Zx>GmCmS-@k-#{*(H$Y}_syE7sjQVUz_{(x+FK;!FF9M02Txo5U=ckFfE9uJnN@=NweAV32au7A(2e?W(hSDpNZ%JQ~vi9gAEF;+~=p^L+NioKR9>_QEBKyi^s@I6gvwL>e%ecjswo=Q-8_zx?h__`dESSz4+*Ug!064K?5BXpwE7dsdB4D*>?Atp#)6O8PVJt(BJFI!Xtvt9t_SCKG8vJ(}+$toT6@8LfUAlJ|x**&f;JfW~Xz_c_GC5JpUy<$TeWjX~gXGoSRDww+J=u#PnR0zEYV)%JDRHtCNjc)7Jq>iL(rgV4+>zPTT%#Iihf=tE+F6Azo28kR4X=l76%iHE`u3*YRL^XI*PQCX5Nd-V@(lAYo3y$7Ge$4U`5Mblr9V4Lbm)N$desQbEK4DpDv$tA+P&5z`(duft`CS5eT@=eQfYLrU6@)0a_W4P+?&D;WIHtum1BGZ_52d=TK3x0>xrksuBm=>s*sG%rp?R66?ASMyoR>Npnj~Yf@IwFVcG5aSL2X&OKrSjzLw`^^oi=0zQ;!cRHNs#>{QpowDL>(E<4kAu?69sYX92nSBTUk7i99Za)2E=x^wiUm}CION=x32{{?D=&QH3Kqa7%{;c0cAYo^d<6qm&tt<t-v>v_$8ePUzpemwef4W}sey;dnDrOj;6_e>^!CVQ(VpL5Mya9MtS^n~5)TQk>BX=+9i<&!4-Mr*2iSx-#4FCZo^b_CjB(4<>a-#za$+95VFi}zX#wg4tsVPi6`T%RK-6mYfJ`YA;M>C^{XXT4ZK^U!VWJ#Ve08hZ^u4j|7Pn1Av`XRoOM`~X+}wht?D>=C@&O?ox%p1v#Mb-QM=EqY)3KJG=GKfO7T+W)!^9cu<(Le_44Kgm9K2f?w1taj^rsxC?4(ZvN@(eFcU<-zD;rP~n{#I9G8bzY&Zg2D}g>hWX;kY9VET#z{B>@*hr2*KqBBq>Wcb1|p!q*E>c&{Ys-T_T#r@IWm&F^pOcl~l$c|2Z?pL;a29Zf>nPDc`1&57Kimr4v$`Qf+dQ1Tp@moM*@#GjI-U3+`9+I}7i8C4x8C92%4rivHa;LDxo)T1N5)>kb=e8=7RfbL)=XYBjYJ;|CP^eDHc(#u~NwmGU#=O`hYIBJ#2Qt+qP^9$qNLUjB{UPUmYYFU^tX-Qx(;f+C*h0h9^j>?C~ozb`l58&$`Qb-j!r9zdh<huHaR@k56*&qeT3K2RJB>PHyhuN4NIlKj(}9*Dy&(^yK+GF_onJlr@grpWAdoO2<iWn~OB%UC`We*^N%x{FMQiiNvd%rbAVoEui_<gAf3>vdv;A394deCfEuRJ~DN!ajZUDj8?xvy+;yqZUXvta#f&)MTrMqJc84Uq+#UQIlX0jTH4-)%uJzS?YlbLcE9=P;u*yZk&tMg>+dHX3<YDRw_=FArPj4g-*E7q=%S~=G^End-l=k(2B`L&a|gorq)t<;>;*yH^rjOCJhbcVzan;<~48E42K!Auy2Xn(lSkkhI>Lpn}XiZ<Vd!DmDYQUkB^X?X(KSE;<8Tu=X~DBCU0p{V2wnBYLs?S@e*=gg~8eJ_|)G+Zd^_2PR7+H+%q1!s=z6av?vj?tz)P1EXmAK+DY;^1H<064<c6Gf94&ENFnDIufaTtQCYSXXj{yo8U~h(X5Y%)zoOVUkN`+GgVj2#$&))e-7Awf?@-q0T)2(PdP!W5_P*FI-b}R=%7M>L>6SA57>NTLhM%@D9p4mG(w<gzG-Q-mm<a+Nf?G9GT9m@U`^1q<TDOl$4C`{r+iHRrAON~JM5^b=m4&H5^OFcz_+RO%uC~-0nlV=|U3ZIeihCc<FTMvIFiY>z5QhuG`%wP8Q{WwrKPc@CpSkmg^4n&iB)pK|O>k%<v$b?VT~S`9Si*cB05t*dMk9m<OzgBF1VH;-Bll)2^QlHdn^GhXED81M9Uh1~ZFUM^=~{WC9@amx3xh%wjudriPjTX_Ud<q3F$rz=L~4h7hS&%gRD&Wv)>_?6MHfo~%bAhlx|LIq0C{i<g*{OXcYX=_GmB7`JL^!%yZKrjjz|q~<ucgQ7H#dDBkf)a?nS2FQ{;gQTk}}qtmTf%Zp!5ZP9Dn~GGLv?S(R=pTO*P0VaRrW=xmb=>s5Ize2<4AB`#TKl_mI6GMs9*4O?8glB*?QRq7$A<O5Ca7nFabWRy&NldzwYzRQ(gMcV*P(X2MF?EeO-!qw#Fm711nZt(LaGV8rys9&nu;*{ZK=(riqG7-jZ{I6n<)-h&R9BWK=#&KNYkl2r<QI-d?kRrtih9szowg5qQ-nyyI_D^**)ne|_R69?4RI1S{mI%s*te7|_Wff_!1R~ST-dMre(2V&6U3sY+Di_0@P<fL?5Z};%aL(I*V4V5~4KT(dzt$kvvrv}6bTHhR-$jpXOv-ANp7sMs#-+5AC8VMtrh=})X-Bdf)JDl@24;?<DUrGi7$F5e9h!SA<tQ{Vr86Zx1Y-PYNG3J|s(VbO<?4|bTf(~Wdj{7c7*G};_%>1&<A*Jb=nz9aHF0!OI%A<6pqE%BhHtdreKq_9oi?{mrICkVl9gh-1W~n#gaf~QD%62@qTw~u*-3!BN)WtCn<Xv7D|2LmLOjh9=0WbRMSQNk#=3F+F7^6u2T9!SPchi9G#My5(C$x&9D?S3Kot!-4?G#^Qs|NkV0yzZW7QJwkSV30F=wA;3M)c)&QDkY2{;<6@k-pb)Sfj$>Pmx;F@milXULojA#cLvZw18j(p>ru%rPdyOg@iy)}9~Aw;6l<@?^-I1LL&_<kLSuzsu@?7ydZQZoE8hyZ29Tgf4@@p}oOhkzlk6b~Ijbv#r472-M>1NPLM{azaIee1pC1Q1xVoZ%aki0N|z?Rr87CZ`*2K2woDs2kR;+51tf;H*RfjsTL)-Kfe#s)^w*4byrk)B}#BuonvRQ7`w}9xeH?AR9IrQ6(Pa}T$aR#YSQDuW|)2@cY@>ivZc>s237xzV2274#7nqTR40^;eC%B3VA8ccH!4gmv#*)O?3I}0j9Mhhe1TRogB|A+QX}36EGY8st?5lBFs7Jdi{K>;vwLdv@^-)s27Q3y&w6{;4z_|vQ>*qIBQXTGDG^B8;nIT5rXg?kxH7`SJ!1z7SwjOZ7lLXs9eA2Rkxiwb2nB`^hcEh$!%9sR7AZ$D&PNQ$BiU0SGh8gkPuM5m07r>yV?6FWvYHf}-RFF5kyKgyo#K_4%^4P+#GQdG`q|iI=%m6nD}77+uU2Z(>SzHnNDcGPQOjm2vAy4v*-=slSM=ykGl({%sc5Auu?<o|pC)oGC6XywTWV3|_2?_{Ye4)V4<^=R4diuOZM~RCH18k+Mi7aAZXL?%vrLHkAox(@C4V|N+2l+sL?f(lo3|buIcZpxyH&x!YEw*hO`D3MrC^0VVSeNz11q&vVofpA&Xjm3R=Xq7s;gc;hjIfnF(aNvE}5g)>4}K+MJB{i_O^ogC};JlJYK5ZE=+^n7X{sN&oaT-*lnTq<YF00T6?U!Bb`hDAeHZiWu-|`1mD4ViuECdr7ja-9)AD<#u9J1Er0{0hQh6_+U#o?5>|p})pj(J?SlAwNE7OfA`MpGC~tY&9dMS5D!A{9>hjA!wrMuJB6&eTuSk9|adKLSQK08TQ;ycO+*?~oY=^auoqOE2tpf9yPyouE5|m-ll~SA?zmO84XYtsfxgI0a8Gl1*0xlL7$7k@nIP@~sW85}6+aIU(G_Go)BiyS-Oga06d0yyRbaV=2;$5^B2Eus8_QHaqN2~JQZ%9RxWIdDsA1AH0Sqh)S`p}L9d}a0sf(WSN+2Mp|wE#UZb(@%nW_fgk2DTI#Z8HLS9LfqYuAE3A5MwCVbe?N&D6_|rva*O6BI+FdYH9bC%N@o#!`|Zz`r{7{1P3bx>gn`GOA3p3N#a3$7?=&az?Dn&M^du&x=l^NaYW@?Os~J02uBdQbl_YX>e#)Krx7KcFL&{p<?amO$69U#6>K8?zCIBF%Q213tcvfJ4x%C2FuBotsvB7|Q%ms|RieL+1Su}L0nCAtFm)wJt>}6XFPw2_3V?+UVqHx;FIrV4PdUT5q;rR$QgBl+$KG(ZONwJG(MgN1qx}`8M)n5r`?beI+egR>GZ*cRD`xh(ogeCo1;ok-x(shICNU<@IbvE=?Sx%gG5vOZ8>2!dhz64rw2kTk60jlXLiz-DhMG;}P@G8*O%{&EA3F0V#B+M#rxE;~0<BEo@5g5!fx`>2tdz2Ss~Z3L_0%8;e<ZT#921VgbQEZ(VFTqciwbAzW8HLn@d)BKIGM6xf=bVCgWE0sGbFsoi|r~vK`8=Z&UY-mTk7wRC1r^0A1>_6XEVYiq`D@V)AQ8S`eR~3-Xzs~mjt+gOc)An7U|tPBR#|VUQGr>CjaOf4f_Ae=!@t?!G;ebigKADpq)<@#}O6}UND+!I|;`E8BmkKM3;zF7Vs|<m%}0xqxM%Yw}J=*YjF#dtyVNV)hNKLiYRqUvn`LwtxIYI+*(7bB`nAR;hG;$rf}IX3QMCO%;+!)+C?*KVb*Lf<gnT*rkBe6DZTbI%4|{(n8Lbf-{!+)y^iLjPMDga1sH2E$7^;TBYRqppQB}?-L-9L_<}_;;mjenZ?o3g9D3pSU88Wg)XQy?_w-%}4%&&|R95BrbLy7M0`o2Ni#PfEnh`lG$^vf`#Onxd3B{{Os#3xZr6>S^bC)B{Tu33mHI}%9ur5<QqJ&_RytA;MoeO)^B3vKU2gfzGmia4ht1r53hQHJIHeQFexdpEvisSez5UM?5j7KMy$68_=Xh!+|sT!n|wgVa|aauZR@IGwdn>PSd-n{*L!5XeWBc!v(1mY^0wdKlrW!iOVUdj$2!K&BC4QG>`RGu3N5o2ZrtE8Li%AwEP7?dT$YpYUP+)Ui!g)%T7uVA@ZKAV^UnFWVzU(*iE_9P2s?w?v=7T9K9W~Nh0=0{hQYe2yX0%3PCH+rI!b*bQXoBk4X^cs`DplCGf=O`M-S@p;{41wK3k9K9<Uu5_A`6$LR1Y_mijOPYC=cMkRx=eUKT_VyL{P5DnSca0J#ZC8%SJ>m~x7BwCF&+x89}FW22cUp#B;WvC>8XC*!!US3-WLrjeFGX@!1_|!8rW=r_fx6j78FeSz&eptU!K}k?lU7fr%LsC@n@b`slhBhvAM(IQn&}3R23zQ&IGiH11AYttqj_&2*7YGlK$j}X&mAg{bT)Z;&`k2G**G)RQ7hoU<&Y3A<<Tbs>l`nP?ej&Fayn<E41QB9m+PQK!cpvzj4`;7I;wxC0pK+`(ls32sSjRF9eWlNP8AyAj(3hfUg#;nmEpIhG7^6(uu0qN`@?(Sa#B5>u4N*%&M)59%|0L;4Z;&?7q5;0Fkv~EU9Lbrb~4Ilp;R`#*o3iu{s-(l#!}=;HZRAVKqJD7DD`#`sUS(S_KO%AYBZvHNB?GK&r7S0x(qX(LhNn@RLoetQ3h+iA`E%bufrqTr+t|6n;sr?`i72dNot5nbJN)yRn@5J0(0jiY<p93}`$y+4j*gQFF_r?4whQzlh+n&Kx6c7A<OsDDq&voR0%oEK9BN4Mx!ye{76b!5|Ysc_p5atH`%~8Ymd|92$Pvc<#Q@Y@mX%_{a&zz6<#s_99u5iz~{(^h)-#aNq5|WxBK*foV(&i{+k}*jfu_^Ba@LT@L5FqO!&TfalAvD3A%s{LA2fLfx2~K|^t^l!pq`j~lPgH{;3S=+yV@Op%YSvIa}uqGN$k5;BR=HB@AT)W~#h@WG)BzoHnit-7YHCW(iHC6NYa!|n<+H`5#eJSNC(elD0C*vA|&%E&hnQ5xdYH2CS9BtaA<^2(Fi099@oSZ$o&T97-a0vp1|DSB|HhzQJo#}Pc=Me{E&aOuFwNy{QJT^4j2G<On&hJNx@D)>(<JH_OmFeLO-zY-+s`$u^SB*SCptk%|lr_jWieWc#@{6QkDpIiXGUf_?AYKWRHD2s8BAcT;yhR~}CQ$&e_32-3*8qCDlS2}KaXZP}5_I=>M#G+|LOYcEa^a6G)del;qV1RW&xQx^zS3DBHfPqooD%U#|J<1Bp71y+<FweE3faBP0U<RAbMQ?D-SB8ubUEjiBNT#r4OYEH^Sgs0(7DH6hDZA!p@zyKGxogfm4^L3PaV0xAqee6+JW5Ar{tZGuu)tfXl+p3Y<-iz}k+93w;JI0w^5`H~QUj#^qh#(F^44=6HR7-ZvXGjwp&1i9-I(J_a<slJw{<)B2@J*}19E2QkrGn)ap`z1Orm+P*B}EA7>m}&BH<lY8?LV@%33LzG|bMCaXipk>VzSOPH0OXfkO;0K6tnT<B?$zi=tP&gaEvrD`G=p8BGIh=aIjE;7}(L*9)hl2cjcgQC=1fun+*)*4$h_^vGwbl&^;7v{$ENL^Mg`m1+y_#Zcr1ioguFr*<=C8tM${dHe`i#*p)1@v>d$QXx8&SS5Gsfiq0wLl!`aoEpJkS~oG>SpZ&6g-K9mO{zwA(IQ%aN|TedOhsqlNttS^)R?{sZ$Ri283-qsNp>h%JD$%Z=1gOzx>7&Q^2lftGbNbjn@$$HYNotTGGQs%tcX$s+iB3Hf~H<>KNYMQaLkzDEbxxBHE3FmHc0DN1#C9z8?)URFzFNw_VV|Mu_H4^2^s;<`2;<U2^Guvp?NCI8YvDQe4W8mrm&6e`6dEkIRQ)gu(dK1OXP)SqoX((acNp6;nO6Drm8A&I2abNxPTm4MPQf}xnI8;*i$hYkqAN%I9Av?ID#rVm!s>R9C7d{2_9-7Ni2YmBTr$vTPhjlBUr5?ui+!gw38=5Dp#i)W6C75B|2D#qQ<S{x&)McMD#ptebjtrd^99da8kEz)t7`KzofG#-ZT^mDs(^jL$Ya@-<v@?61U-K!L|<EY@h7Xr~*u5F^P;<V1B>TZwkU(rA#5E-kMU5<Y4yegcLZRWl*9!r#d&N^SCj1S%~h7fhQSG98=oZ)0#pzCe_rH%F_(35>xI@@70_$;U)+f995M~&R%4zQx3Fx0r(dcgzBVpYU<u*c}B6T6R9CX<r43%Q2>i2@|r!B)6_2u5GV^t0T`3-StGX|uLG5Xk5`wgOY9SJ5I~<44XLa;19T4M{)~=>NUs#9t2U&8<wrm`ZYR$(GlzSfM{fK!8IihC_;OLSfYn=9q!psU)6OEayvpwqoyu^w4PUZc4o(G&u8tpYC>v9jlU}%JOXg%y)sTKUi$fzj>Z<8Hy;eatnME@tE{2MLTOK1jWLZk4O&h>DI&+4v&K%7FGk2IZt&oD&&PcXwgK~q#12geZ(i_(;M1$2Je)C$c(efi88?Di@*F9HE{3QoHoS^hYxaX%fvu0B{C#lFG!C}a6{CkQkU4SUg?6F8=ZGU(~LEG?R3wj~dkvnx`6-AdaVTMbw<uB1dVJzd#%1#K&Jyrc>QRf(nQ8sttJfgnwL~f-ZHEGa;D%+qy>U8d6OYd*>ZQ=ezytAXOvT7Feg8&SAvrcfzw|x@^iY5*nKIBY#`u$__&}B^%ClguVqjVxXU*w4DK0Ii>OaLEwWfJ<NnL;n~Q8`u>=UOwLRYPW~UMB7Xy+T~O0^#ahw#jW}(ssodugQx68_H58FNbtUPU7MMdziAMdjhC@n*E+2R8xq-JHABA%q^R$N1oElk;;PN?K>fg#A-)8)yOo5paX4#7ZEeOam2K{6k929^_CboDxV9w;xZa`(#I?;l|#5Srq*eT=C<|aB21)x{nG4e45&&&Vt}M*$d1qXe;Ey$Tye%_%`gnTE|hzHy_v=3&UJOT=7dd~X@uXD?nCmV^mt~vv4z?RM(H6HleXlAa`LIiJ%C&1*(6nxO6^27FJ6SIC18vTh_gtCI@&bxZ?GP3>YN!NV$iAMX5vS*gEkAHsxP{I@(Bhih3RE3Mc3?aESoxW)m8kE+gMRa3c!^`%x#nYOjSb-ZOSg4qs_IF!%A!lC&@{xHVt;x=E)BnS>*_FH<*GocJ*`9pI*jA^`>sMuG&841zOgqcnF8q<5Qv2G81Y!a$x`5$=oHv9j$iqNp~JobBj5$EPRoJ1rhZyXMyyT;zud(sW!;GNzx9v(lIVNBt5o0O)8gtL#0#tG#uJgP$5jtnaWu?RL6l*4Oqy0+OvSuuofi;41{1l3|xqRW^q8C9kqw20w)JG7S6#RTJjq|E)R=70SC;rjR2uOg6`k8891yejC5-D)&Lex73elT?lb3@Y?9Ut&uerAjHuT*$yL7bXg1~UPwm1e0CrQ2TKQhA@I6z;k#44;@8mQKpf`JOxW&_^lxp=@MutR;GjgvhQAb9d4wWSH>m8zqc_(mEhp!(?Z-@(DA+Zpn1`B}M!1%llw?B99oj56bhw%-d3J5J4D}Uu7RUd|!(_DE=F^;B89nC6hOHk4xp1J7lg4iqUfriP8P?+>}saLNwx^1jr@qFZrbHoAZ#Ywep`xr09pk<ehps;cP5y%)0gqbnD08KuTG<cMbB2yxmbP6%9NM}jQCbfFJM=Nm_(+)qSKHe1yCGSXH>7M6c*@fB>mcnxCM$X&c!RUgLM*@WBO=oy;N-iQS>%pjGjD#Q<XHtQcTuGO>*QqrG<i8kT)Bc5WsJ*L)p#ok<Wuv)KzqGj_WmBTK*p^_mcjCCn5c#HZU$Y*D_ZTU;|E`L`cN#<Cz=EkKLv`PVL6-`#CR$I-Hj)x0s^cM5hl{-oLlTkc>e;Pi8iPxu-ik62X_Z@i(S%39NCO4QU?H7aLL~~}qq!Q!_(`nGe*$)#mA7$MwZtsp?R+0ifnKH>6aO#4E9Qc-4-U_%LmEo-Ab{bqP0l2cLF@w?8{|Q3YYBCsW1B)Ss#vM$2x<JL{bq*~1#LD12I1+Ju&4yeSXIS-$>2OxZbsNkhy=)vXz_sZbzWT?uW(d=;WRF0!9-gd)mODFRFrv*soa`W9xqaj`ci3g2!pY8SD>j9`z%^Y!a-w(aC!-E;(HCPgJ~n)t(jop8Mcz-PRqWH<KAi>=aZCs;^HH^9<&P*3d{}ttR=Em;=5sbCrD03h?+IDUBO&PTMAaU?pa1lpviL3bn7;j5{QsTAb2{LpkLCZ#uy<FK$QYOjX}O`X+sZIMwyB=63l5*V|E!c<__aMoBJP3jnS>Dx4I@66%mXfHwKO1NE-hNp=5y5CnCcsx>F}YC}23Af~+AGJDW{m<*H5q5u%Hyq~E8Ax&C-BY1@#e-f)X5_nn;bOIDBO`SQ&PPgGCsTA{9mvxcK)r36S3dr{3UyoW(1VPRx+(Ph5zbX9)&(~s}176juKFUyi5$s^wAoMzRL39J}%OV)TY$K=JVZR(o0;~P<X&r44#ZZ``jDWhAlj3R{{P4c>S>=shGQWsej&?<dRIUz-s({b`cO{BQ(gpeMxMWNpqPB!(RL_0FtlZxn`O^nx9IXUNRyO6lcFUt*qYswt!d+%tSq6Ob7?U<&jZyL?GxwIfXTzR^nVz!O#1+rKm02hrJ=XtH2EN*@I*b18t+$fy3MEFiEIXioM)d?$f8{|{4PScasfROc}j?kg#nyN4o>hv{rcbdCG67xz7=33Q2NskXsMS+UyIR{R3fa+EMcv@pzk^uOmh5DHh$c6iG1*N*>0pIp|z#v%)HN%*bwn*Q;rH*R(f|8kL6-|$bKHjX}={hnmo~{w6Cs4`kJcHDDp<Q^P44^hzC+RMhA`mFGqK?_B8e^r|T}g4!QYyU7AU+yfE_*8qgI4(UK0yusH?>xKGd^47qx*hTAi&h3<(??(^L~v2NM<I*AY0|rmr-LWsAZMCo;szv`@M8+2FTnHfnaJ<O|m}a{GwozDD9PSUr*SE>4s6@Z%moWENeXCp!LzH6X_^&(UYf8W+L0O6bT;uzpho(E>K9tF{Hb>MQ}nI4Y{<l^&yrc?SaxJvMAKxXcdoN+G><Su}+~#pi4^QuGd>>ptlfXs8_VK;~_eXy5!A{R%m-PyV^FlSJ&I+O`}-Xqr1#;S$yu^E9-DXq+onA#54hi6r{w+&dtzdot8aoc0MAmhf^Y37}{97mkKvDkcab1@YOrIoW46B19Rn@>Y0eJv`_V+J6UK>u8n5wv&i?EFTOM4yJ*?;W|i$y5i`oZdFTG>zGUilgBP9_JXxLF_)u0P)i;21YLIgG6gz4byqzs%xiJg9io3qf(Kv~RcOiGa9e=joj?U|rm9?>4R@hmwWDqlqeM9b@dOETFz&cYli|TPT)<FuGu}y72M}bGGEF8PBU`K?F)qd2iYTdf%5aTJiJb;>*Yut20&7~<JlwqE=g-4kQWcIXQfXMcbtvx6jVI?=&4V4P4j?bK+Ku1sDw6z%7qazilG|m8AK#=Ll)&YO$v3WASt-Zy?5*BtA4dQ!YSP45YB}ztnR8oPa>q7}AZ{VDbq<#3v4;kItDMxu6CS_0^PG|V6TBFo-=Vcc@BM>O6y8W(W*LlwBCaSX-=>0?}F-4p@hZ@!Q(P1q-tbytB_?MyrC%BhYv4lHaUcvBJK7YQDp5`OeJIF}#UbV-sXg5()-J?SX22D*?O*F~Aq>!h96!qDX%)g?!&sIV6{94;=3q)k-GBJjID$uwl?Vl#CRVq;Sfh-g(IG~`i0CN<Il3<dqw%fJH2KIz=jIdNFP>U#BTARs@%DwS=4XB!2s+Kzktv1_&+A|SJWcoYXr-H61ZZ}g&@E>Um{5@x1jUPtOtdTJZt?KUqZ2n{$C(rv{A~dA$t<o&ej{m*Q-xNy%xA1x*633ywB(Ayz^s~GWn+<-zg5uE8K{BA3%Gw_3QV(}x+X|}1Hyb5IoCpQihcXDD>*W0<+M$X`3JeA^ROBTwj*u3r^c%*+%2|&OMi1LMUZB&BL=sBKl&N|Q<4yVqfC-5x#%^n96frSrT^UvnEVWXTS&)16i?AuOQfVv)*Ob2T(HNCN%J>C$@-;Tbe&rdXV|hK<2WyLLGNYL$E^S2BTUxy5psx=59DRKMK~W#&`r5dhShe$D<g2LaC&TgG7dr8ZDn19<rXwyT`KzPy2v`;30f=hi8p2*RXo1mda7!@t(k^wi{_u~7l1ETz^KBVtvXfq>gQqplb4GGoi4IQIy@htN-n%$ebRVgaFt0J18QWlV_)gYXYa9u6ndJZD=nL)Yp8uG>n`83eusRRROVI%Xs`vNX^r7XW(>$v)!+z=EP;*w)M@iU=BHArJNY9vXP;S1i#naRO2fnyNRs')).decode("utf-8"))
_ITEMS = (
    "WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG",
    "MILK", "WOOL", "FERTILIZER", "GOOSE", "COW", "SHEEP",
)
_PRODUCTS = _ITEMS[:9]
_CROPS = _ITEMS[:5]
_SEED_COST = {"WHEAT": 10, "CARROT": 20, "TOMATO": 50, "STRAWBERRY": 100, "MELON": 80}
_ANIMAL_COST = {"GOOSE": 300, "COW": 400, "SHEEP": 500}
_LAND_COST = (1000, 2000, 4000)
_SEGMENT_TURNS = 72
_DECISION_STEP = 360
_TURNS = 719
_STATE = {
    0: {"last_step": -1, "route": 0},
    1: {"last_step": -1, "route": 0},
}


def _get(value, key, default=None):
    if isinstance(value, dict):
        return value.get(key, default)
    getter = getattr(value, "get", None)
    if callable(getter):
        return getter(key, default)
    return getattr(value, key, default)


def _seat(observation):
    return 1 if int(_get(observation, "player", 0) or 0) == 1 else 0


def _farm(observation, seat):
    farms = list(_get(observation, "farms", []) or [])
    return farms[seat] if seat < len(farms) else {}


def _copy_action(action):
    action = copy.deepcopy(action or {})
    return {
        "farmer": list(action.get("farmer") or ["PASS"]),
        "hands": [list(order or ["PASS"]) for order in (action.get("hands") or [])],
        "market": [list(order) for order in (action.get("market") or [])],
    }


def _plant_tiles(farm):
    result = 0
    for row in (_get(farm, "tiles", []) or []):
        for tile in row or []:
            if isinstance(tile, str):
                result += tile == "PLANT"
            elif tile is not None:
                result += _get(tile, "kind") == "PLANT" or bool(_get(tile, "crop"))
    return result


def _select_route(observation, seat):
    town = _get(observation, "town", {}) or {}
    shops = list(_get(town, "unlocked_shops", []) or [])
    if not shops:
        return 0
    market = _get(observation, "market", {}) or {}
    inventory = _get(market, "inventory", {}) or {}
    if shops[0] == "BAKERY" and float(_get(inventory, "FERTILIZER", 0) or 0) <= 10232.5:
        return 1
    if shops[0] == "PET_CAFE":
        rival = _farm(observation, 1 - seat)
        if float(_plant_tiles(rival)) <= 64.5:
            return 1
    return 0


def _quantity(order):
    try:
        return max(1, int(order[2])) if len(order) >= 3 else 1
    except (TypeError, ValueError):
        return 1


def _fib(index):
    previous, current = 1, 1
    for _ in range(max(0, int(index))):
        previous, current = current, previous + current
    return previous


def _existing_sale(action, item):
    return sum(
        max(0, int(order[2]))
        for order in (action.get("market") or [])
        if len(order) >= 3 and order[0] == "SELL" and order[1] == item
    )


def _owned_in_hands(observation, item):
    private = _get(observation, "private", {}) or {}
    inventories = list(_get(private, "inventories", []) or [])
    farm = _farm(observation, _seat(observation))
    n_units = 1 + len(_get(farm, "hands", []) or [])
    total = 0
    for carried in inventories[:min(n_units, 40)]:
        total += max(0, int(_get(carried or {}, item, 0) or 0))
    return total


def _requirements(observation, route, start, end):
    market = _get(observation, "market", {}) or {}
    prices = _get(market, "prices", {}) or {}
    farm = _farm(observation, _seat(observation))
    quadrants = len(_get(farm, "unlocked_quadrants", []) or [])
    balances = {item: 0 for item in _ITEMS}
    starting = {item: 0 for item in _ITEMS}
    hires_by_day = [0] * 6
    purchase_budget = 0.0

    for step in range(start, end):
        action = _ROUTES[route][step]
        units = [action.get("farmer", ["PASS"]), *list(action.get("hands") or [])]
        for operation in units:
            if not operation:
                continue
            if operation[0] == "FEED":
                balances["WHEAT"] -= 1
                starting["WHEAT"] = max(starting["WHEAT"], -balances["WHEAT"])
            elif operation[0] == "FERTILIZE":
                balances["FERTILIZER"] -= 1
                starting["FERTILIZER"] = max(starting["FERTILIZER"], -balances["FERTILIZER"])
            elif operation[0] == "PLACE" and len(operation) >= 2 and operation[1] in balances:
                item = operation[1]
                balances[item] -= _quantity(operation)
                starting[item] = max(starting[item], -balances[item])

        for order in action.get("market") or []:
            if not order:
                continue
            kind = order[0]
            item = order[1] if len(order) >= 2 else ""
            quantity = _quantity(order)
            if kind == "HIRE":
                day = min(5, max(0, (step - start) // 24))
                hires_by_day[day] += 1
            elif kind == "BUY_LAND":
                extra = quadrants - 1
                if 0 <= extra < 3:
                    purchase_budget += _LAND_COST[extra]
                    quadrants += 1
            elif kind == "BUY_SEED" and item in _SEED_COST:
                purchase_budget += _SEED_COST[item] * quantity
            elif kind == "BUY_PRODUCT" and item in {"WHEAT", "FERTILIZER"}:
                purchase_budget += float(_get(prices, item, 0) or 0) * quantity
                balances[item] += quantity
            elif kind == "BUY_ANIMAL" and item in _ANIMAL_COST:
                purchase_budget += _ANIMAL_COST[item] * quantity
                balances[item] += quantity

    first_hire = max(0, int(_get(farm, "hires_today", 0) or 0))
    for day, count in enumerate(hires_by_day):
        offset = first_hire if day == 0 else 0
        for index in range(count):
            purchase_budget += _fib(offset + index)
    return purchase_budget, starting


def _add_budget_sale(action, item, quantity, max_orders):
    if quantity <= 0:
        return True
    for order in action["market"]:
        if len(order) >= 3 and order[0] == "SELL" and order[1] == item:
            order[2] = max(0, int(order[2])) + quantity
            return True
    if len(action["market"]) >= max_orders:
        return False
    action["market"].append(["SELL", item, quantity])
    return True


def _budget_guard(action, observation, route, step):
    if step % _SEGMENT_TURNS != 0:
        return action
    end = min(_TURNS, step + _SEGMENT_TURNS)
    purchase_budget, starting = _requirements(observation, route, step, end)
    private = _get(observation, "private", {}) or {}
    shed = _get(private, "shed", {}) or {}
    market = _get(observation, "market", {}) or {}
    prices = _get(market, "prices", {}) or {}
    farm = _farm(observation, _seat(observation))
    available_cash = float(_get(farm, "money", 0) or 0)
    for item in _PRODUCTS:
        sold = min(max(0, int(_get(shed, item, 0) or 0)), _existing_sale(action, item))
        available_cash += sold * float(_get(prices, item, 0) or 0)
    shortfall = purchase_budget - available_cash
    if shortfall <= 0:
        return action

    candidates = []
    for order_index, item in enumerate(_PRODUCTS):
        price = int(_get(prices, item, 0) or 0)
        if price < 2:
            continue
        protected_shed = max(0, starting[item] - _owned_in_hands(observation, item))
        available = max(
            0,
            int(_get(shed, item, 0) or 0) - protected_shed - _existing_sale(action, item),
        )
        if available > 0:
            candidates.append((item, available, price, order_index))
    candidates.sort(key=lambda candidate: (-candidate[2], candidate[3]))

    result = _copy_action(action)
    added = False
    for item, available, price, _ in candidates:
        if shortfall <= 0:
            break
        needed = int(math.ceil(shortfall / price))
        quantity = min(available, needed)
        if _add_budget_sale(result, item, quantity, 10):
            shortfall -= quantity * price
            added = True
    if added:
        sales = [order for order in result["market"] if order and order[0] == "SELL"]
        others = [order for order in result["market"] if not order or order[0] != "SELL"]
        result["market"] = sales + others
    return result


def agent(observation, configuration=None):
    del configuration
    try:
        seat = _seat(observation)
        step = int(_get(observation, "step", 0) or 0)
        state = _STATE[seat]
        if step == 0 or step < int(state.get("last_step", -1)):
            state = {"last_step": -1, "route": 0}
            _STATE[seat] = state
        if not 0 <= step < _TURNS:
            farm = _farm(observation, seat)
            return {
                "farmer": ["PASS"],
                "hands": [["PASS"] for _ in (_get(farm, "hands", []) or [])],
                "market": [],
            }
        if step == _DECISION_STEP:
            state["route"] = _select_route(observation, seat)
        route = int(state.get("route", 0))
        action = _copy_action(_ROUTES[route][step])
        action = _budget_guard(action, observation, route, step)
        state["last_step"] = step
        return action
    except Exception:
        farm = _farm(observation, _seat(observation))
        return {
            "farmer": ["PASS"],
            "hands": [["PASS"] for _ in (_get(farm, "hands", []) or [])],
            "market": [],
        }

# Locally developed execution overlay for Arlene's public three-day router.
# The embedded farm routes and cash guard above are third-party code, Apache-2.0.
_ROUTER_PARENT = agent
# Reinsert the final agent binding last for Kaggle's source-file loader.
del agent
SALE_LEAD = 2
SALE_START = 240
SALE_BATCH = 1000
SALE_FRACTION = 1.0
SALE_FLOOR = 0.0
SALE_SKIP_DEMAND = True
SALE_DEBT = True
SEED_TRIM = True
FINAL_SELL_ALL = True
FINAL_RETURN = True
FINAL_NO_LATE_COLLECTION = True
_ADJUST_STATE = {}
_PREMIUM_ITEMS = ('MELON','MILK','STRAWBERRY','WOOL')
_DEMAND_ITEMS = {
    'BAKERY': ('EGG','WHEAT'), 'PIZZA_SHOP': ('MILK','TOMATO','WHEAT'),
    'BRUNCH_SPOT': ('EGG','WHEAT','STRAWBERRY'), 'YARN_STORE': ('WOOL',),
    'ICE_CREAM_SHOP': ('STRAWBERRY','MILK','WHEAT'), 'PET_CAFE': ('CARROT',),
    'SMOOTHIE_SHOP': ('STRAWBERRY','MILK'),
    'FARMERS_MARKET': ('WHEAT','CARROT','TOMATO','STRAWBERRY')}
_BASE_PRICES = {'WHEAT':25,'CARROT':35,'TOMATO':60,'STRAWBERRY':120,
                'MELON':250,'EGG':50,'MILK':160,'WOOL':200,'FERTILIZER':100}


def _shed_positions(farm):
    n = len(farm['tiles'])//2
    return ((n-1,n-1),(n,n-1),(n-1,n),(n,n))


def _l1(a,b):
    return abs(a[0]-b[0])+abs(a[1]-b[1])


def _move(a,b):
    if a[0] < b[0]: return ['EAST']
    if a[0] > b[0]: return ['WEST']
    if a[1] < b[1]: return ['SOUTH']
    if a[1] > b[1]: return ['NORTH']
    return ['PASS']


def _shed_projection(obs, action):
    farm = _farm(obs,_seat(obs))
    shed = dict(obs['private']['shed'])
    bags = obs['private']['inventories']
    access = _shed_positions(farm)
    for i,(pos,op) in enumerate(zip([farm['farmer']]+farm['hands'],[action['farmer']]+action['hands'])):
        if tuple(pos) not in access: continue
        inv = bags[i]
        if op[0]=='PICKUP':
            item=op[1]
            shed[item]=max(0,shed.get(item,0)-(op[2] if len(op)>2 else 1))
        elif op[0]=='DROP':
            for item,n in inv.items():
                shed[item]=shed.get(item,0)+min(n,max(0,100-sum(shed.values())))
        elif op[0]=='PLACE' and op[1] in _PRODUCTS:
            item=op[1];n=min(inv.get(item,0),op[2] if len(op)>2 else 1)
            shed[item]=shed.get(item,0)+min(n,max(0,100-sum(shed.values())))
    return shed


def _sale_adjust(obs,action,step,tape,state):
    market=action['market']
    due=state['due']
    if SALE_DEBT:
        adjusted=[]
        for raw in market:
            op=list(raw)
            if len(op)>2 and op[0]=='SELL' and due.get(op[1],0)>0:
                n=min(op[2],due[op[1]])
                op[2]-=n;due[op[1]]-=n
                if op[2]<=0:continue
            adjusted.append(op)
        market=adjusted
    if SALE_LEAD and SALE_START<=step<714:
        future={}
        for s in range(step+1,min(719,step+SALE_LEAD+1)):
            for op in tape[s]['market']:
                if len(op)>2 and op[0]=='SELL' and op[1] in _PREMIUM_ITEMS:
                    future[op[1]]=future.get(op[1],0)+op[2]
        shed=_shed_projection(obs,action)
        prices=obs['market']['prices']
        shops=obs['town']['unlocked_shops']
        for item in _PREMIUM_ITEMS:
            if SALE_SKIP_DEMAND and (step%24==0 or (step%4==0 and any(item in _DEMAND_ITEMS.get(s,()) for s in shops))):
                continue
            if prices[item] < _BASE_PRICES[item]*SALE_FLOOR:
                continue
            pending=due.get(item,0) if SALE_DEBT else 0
            want=max(0,future.get(item,0)-pending)
            already=sum(o[2] for o in market if len(o)>2 and o[:2]==['SELL',item])
            n=min(max(0,shed.get(item,0)-already),want,SALE_BATCH,max(1,int(want*SALE_FRACTION)))
            if n<=0:continue
            existing=next((o for o in market if len(o)>2 and o[:2]==['SELL',item]),None)
            if existing is not None:
                existing[2]+=n
            elif len(market)<10:
                market.append(['SELL',item,n])
            else:
                continue
            if SALE_DEBT:due[item]=pending+n
    action['market']=market
    return action


def _trim_seed_buffer(obs,action,step,tape):
    if not SEED_TRIM or step<576:
        return action
    future={}
    for s in range(step+1,719):
        a=tape[s]
        for op in [a['farmer']]+a['hands']:
            if len(op)>1 and op[0]=='PLANT':
                future[op[1]]=future.get(op[1],0)+1
    seeds=dict(obs['private']['seeds'])
    for op in [action['farmer']]+action['hands']:
        if len(op)>1 and op[0]=='PLANT':
            seeds[op[1]]=max(0,seeds.get(op[1],0)-1)
    market=[]
    for raw in action['market']:
        op=list(raw)
        if len(op)>2 and op[0]=='BUY_SEED':
            crop=op[1]
            op[2]=min(op[2],max(0,future.get(crop,0)-seeds.get(crop,0)))
            if op[2]<=0:continue
            seeds[crop]=seeds.get(crop,0)+op[2]
        market.append(op)
    action['market']=market
    return action


def _terminal_return(obs,action,step):
    if not FINAL_RETURN or step<696:
        return action
    farm=_farm(obs,_seat(obs));bags=obs['private']['inventories'];access=_shed_positions(farm)
    units=[action['farmer']]+action['hands']
    for i,(pos,op) in enumerate(zip([farm['farmer']]+farm['hands'],units)):
        home=min(access,key=lambda p:_l1(pos,p));dist=_l1(pos,home)
        # A fresh harvest requires its own action, the trip home, and a DROP.
        # Do not create cargo after the last feasible collection time.
        if FINAL_NO_LATE_COLLECTION and op[0] in ('HARVEST','COLLECT_FERTILIZER','PICKUP') and 719-step<dist+2:
            units[i]=['PASS']
        if not any(n>0 and item in _PRODUCTS for item,n in bags[i].items()):continue
        if 719-step<=dist+1:
            units[i]=_move(pos,home) if dist else ['DROP']
    action['farmer'],action['hands']=units[0],units[1:]
    return action


def _early_feed_reserve(obs, action, step, state):
    # On day 8 the farmer needs four wheat at turn 196, before that turn's
    # market executes. Move at most one unit of the scheduled purchase forward.
    if step == 195:
        have = _shed_projection(obs, action).get('WHEAT', 0)
        buying = sum(o[2] for o in action['market']
                     if len(o) > 2 and o[:2] == ['BUY_PRODUCT', 'WHEAT'])
        advance = min(1, max(0, 4 - have - buying))
        if advance and len(action['market']) < 10:
            # Preserve funding priority for the route's animal purchases.
            action['market'].append(['BUY_PRODUCT', 'WHEAT', advance])
            state['feed_advance'] = advance
    elif step == 196 and state.get('feed_advance', 0):
        if obs['private']['shed'].get('WHEAT', 0) >= 4:
            for order in action['market']:
                if len(order) > 2 and order[:2] == ['BUY_PRODUCT', 'WHEAT']:
                    order[2] = max(0, order[2] - state['feed_advance'])
                    break
        state['feed_advance'] = 0
    return action


def agent(obs,configuration=None):
    action=_ROUTER_PARENT(obs,configuration)
    step=int(obs['step']);seat=_seat(obs)
    state=_ADJUST_STATE.get(seat)
    if state is None or step<=state['last']:
        state={'last':step,'due':{}}
        _ADJUST_STATE[seat]=state
    state['last']=step
    tape=_ROUTES[_STATE[seat]['route']]
    action=_early_feed_reserve(obs,action,step,state)
    action=_trim_seed_buffer(obs,action,step,tape)
    action=_sale_adjust(obs,action,step,tape,state)
    action=_terminal_return(obs,action,step)
    if FINAL_SELL_ALL and step==718:
        action['market']=[['SELL',item,10000] for item in _PRODUCTS]
    return action
