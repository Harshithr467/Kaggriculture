# Kaggriculture replay-informed submission, frozen 2026-09-09.
# Execution runner and cash guard adapted from Arlene (lynnsakurai),
# https://www.kaggle.com/code/lynnsakurai/farming-score-v3-replay-revised
# Arlene's public Python source is Apache-2.0; its notice is retained below.
# Farm programs reconstructed from user-supplied competitive replays:
# Fih, episode 106687524, and yuki0731, episode 106667639.
# Those replay programs replace the original public action tapes.
# Local changes: public-observation opening and livestock decisions, compatible
# animal substitutions, cargo-aware sales, idle-worker structure recovery,
# feed-shortage recovery, seed budgeting, and final-turn liquidation.
# Runtime: Python standard library only; no files, network, seeds, or player IDs.
# Replay reconstruction is not the opponents' private source code.
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

"""Single-file Kaggriculture agent with replay-informed farm programs."""

from __future__ import annotations

import base64
import copy
import json
import math
import zlib


_ROUTES = json.loads(zlib.decompress(base64.b85decode(b'c-ri}Pmg3rlI{0hxUK~=A~RW~T{W3+nt1Fkf@~`AG)OcC&=Uj*Pm7Uug1);*=AVeTcI;=z%x^S%Fj`e2D>ANMcXN09bL^ad{n!8JtN-oa{{4Ua_kaKDfBM(2e*FCN&tE-%`09WExBv5h{l9+w#jij9kAM63|Kq>^-@pF+uV4M?m;d(nAAkDt-7nw%?W+%8o&Nmv`PYB%j?W+d^{bzse)wVgyX@o7|L=#(Xa4oePk;M!{!sgyAAb9vKY#zz(^u{fzkSW;zkdIh&%Zt3+b^fDJ{-cYfBy5+(~rOX$7a+&fBEHl)W1&N_uu~4Uw(Z3s^7lobvDnhc=^-yr!U`m^Q89=z6|B+kr!V_&-&9Z-~aI4-+%qc-+uY+)t!gEOzPFcHs4ad;18d_eKOuJtpDau^>a>7KmYCbAHMxuywd9@-C2A8;_bZ0z3}tX(|5oA|6iVd`0`g_BHQ`m5&ZhjfBoD0w<W*XtWGtgyX}zPCRUh|c-q_0PM`nw^wajI-=_(t{lEM+lB*}2|M>jPZ<B4=s`ZL5_Hgyw_Z7|O`uv&e8EP+jv^HyE<A+}6Z?eKyUu4ez`Tyd6x_a*0IUL^m^$RYZ_jW{ziGMp?E=Ldy%6o2@@3`D?nzzrdruo>IW?Jt!-J4JEG4EoXY2IHx-G1=aRk+Q>AL_@#eAgR|uEO|&Vq(Pwa>EIQ1$`Yr_1MOQp1<3fP;n(KP3ZPftuKbJ+x#%{g{~(#^Dt{aM_hkm8S5KnJ5c$n!Hs<$*6aTn-xBZN_rHDpFXv0X{P4rmw}1Qle|h@pZ{Pp${r|E(;@-bWez4>43O_#i&Nt6s^J}^9UW1m4kN&#fv%n=>E>EAgD}266w~ne4p=DlRHoN?$$)m+9J7>+?Zj8Z2dX5?|m_H}X<m_BIf6Z-%DfaKuc;8Q&7u(u-wCB@d<*ZKj-GZINvp(lmHn?4u)@J9MF0SzZKa~D$|KYyMNQJ|_OgWYJE#^~d8;e&j1=@6RWzJ%CFVpkNOJ5~|==(~$fC=7&oy*g!G9=~r?Ad&E2wJl#+{CrfTILGj{Nik`x{Ns3^5s>!R}A;<3;+E2r~i4D&wyEew}MIVWli_{uouEudmS#)LryST`pApsEu7w~J0N$a^7R%s#l0>(yhjIBlHj_=z(?D_Oz;dA`NMKr=?g^`{M9Iob%F_q<J`p&xot+G;hG%Vsff}Sp(2U(Q?C+`dLzY+9Lj->?0@%J&2w$9=cqJMykN2)X3HRsjLyv)=R6MhJQr7&%<Ph^)*?jbRW4fHb=Q`5eD17Md`ErHwzIYI+Pkb=>DSs;WzDOA3V7$AV5(={NO15s(<yF<ef<*kZkEY3Tt+s~`V#cMTV@SMj?mG66dfGWBRXat(Yj-);-<;_7yfwac^G*Ee`CbQ`5pv$Vdw8n@hj!`+iUYSxuOsWPa9nO!fP`gG;!lHtV-Lhdzia*jY`g5sU`Gx{G!O7Ue?IDdd~z~NsKZ>7N<V1-OQY;O%-k5EJ^ON&T>xT`?hI}mJ1?sAOp9mZFcW-E<6!-s&@8gqa%`4O(y<{y2Y_z=2l`L_IO`WEU8V836To`D-kd9VPE^XT1i!8MN@K4(6|Q^3lZ?Fg<2-$EyaV3G>=nzrSEeG-cQ0e-U70esrNW}33$$TKYjVJ>zIfL;9;K4;ymbDnSA>AJh3`<#(ZER`WNk*VXRxO=hY6+KC0)&d9~U<8=|HVZZLcbIo^40ZRmlE6}W{<NDFXw$Ev5q6N(*|aUCZ<NT(hze?EUAgU7ty|3Cljr_ZN9J^l34e^cnDB60A(UT=5&#kaw)@#Ve4jlv!^%jfy1uQ>JHmBS%7#Q+|_X|zt#N5QD`DqorENleDL+O|-t+%7uB+U6jHyIKxskW4900A(kG=Wv>GTZL?WwTND<Y+!AENj+LRj@Owj!}sz%tmr;2EyXUt?Co7np3FBF-HCm~Rs+i|97uE~)LNNOKks~byJXPs511A8Q&I{t9dlBhN7mkteC6c)5Ps1<gAh@c4&sH&1S8lXZTg;8|MKP6&)yvp|0kKS<|wgR`aXb{`{&oY;=8ZxrrJ2c?`tU%fA7D-q+kvGfd1O|g-jMY`Uv6M)Hs!wNi74`Ee@T#$-0a3nCMUT>dBYhK+lPj@uPTB>=1z13Wfk}x#Hxw^s+<)^roNIjqN<FSKh4qZkIGE@5@V@$W2|N?ZvRSJZVaQQuv^Lj~$MdI)rUk`*Jo*KejxBsN;tYytw@D(}sslI#ph}TkK+$jHs3v3+Rg_71-sMhx(?Nq8HjCKA2=CO2ZM)p-C&?RF_MAbOEPo>107J?XvgM9A%GdFMN`bD<On;f_ZB248}VE?2vU0!q6;i>S3_9|7y+#vbd6FukU&!xl%ZA{WLSOFdy%=7h~8t{f6@5Y+{SmPwzL^#!Xty#mDcBjnJFhdXFqUJf!NH#xNn?Dg|E8uDA?`)oasU?A|^Yyc?B2cyT2~2uY5@8!-atw=K~Jfd(gw7`LILaYNM;7|ISs)$crK8w_3*abb9XA!^+kALGBXU2GlCENJFzK(X&|{220!k2PB45D=ePby>QxE`^;Im-7!*koZ1l-+litb-<D`3W@ZM8qKBcr?CI?PoefWa;n4e@V1(~h9bYXbHQp$UsYrWE2njwv4PSP1|MpSdpOSG>$nPQ`OZr#WspRbX@X65dN<CY8^(pB@NZ|Nx)Unh=#jI!UxE<(IHM4~_UBeYG+B)jU7EcV`-g{FIZ)K&7`u?tI+c!{$6xezJN)JQAO7oCA0DefDSZ5@WED$kUcKz)+wKnOv{ez6SUOzIl%(N<vJD8Qvg#P150vK??|vF#q?`1guI{m?;PYM=#$I-yx`IkVR{+guD?bm$u7ly9><+U@E<TJZ@IO_UGN>x|5j$cmm#*igSf<nMoj!v`ffQP2Ph>M8dy=fy*|Dnk64Yw5$ebdQ%C6P=D4tixDB?7x!J@VYkp@8uuwKX+2cuhdVk$({aP5eoSswLclC4#JNScv0Tx_#}iqx~99uTcT3h+|ISQ*c7-47uAow({^h8u_1)F5eNGq5=WiO6j-KwGQaT2a>KiJ8$vi$mCAXbA1Lq57q~E_W5Zj3t5lvD`Q@yh(?Y8NSBL&MG{XkEieR=OXX0-Ykw?6Ey-Bm`VuG&mO_3AL%kql;iyLJSGAXAlQ`>WvZI->dfD@tB4yca~df<v}tduc)tavB{UUaT}6y91O;k*$mbl?<v?yP5BM4fd4(ap@4>lBEL1*7tCaLMsA=Vk%N=wi7X8nT%WV07A}PZO+U;@`+7&#JP|;SNRBRpsx1|i|?b^1Qtp?ICZD8A_y$RRUEN%JY@;VLUp@pBKKDbdkqGd5dMv}hKT*NDS2{9kBi^#*E4OMs|xqB?y$L6dU7-)%ERlRFa?pR<V6FCH7YuMMY#8xKW)JFruoa|}#6tBz7fj2k9Ft0Lmas4?uB;u9!h)JKy#MuY8lGrHUmc(mmmBz>cQVW#XSA2Y)<6m9wK(t1eP;QA!Bw@esrqTuMJ~YN?+S$?(S5#2<iXHc&%&>SGd`_<gy&h{Av*>n`8zs<AI|hm+oRMIWjIi4<UG)<N23%bq<t1&XSe0|8YJ9KrHlwsq!_xmxL>OYWd&3j`@kQ1-<}8X1wr-044Q=ouF!xvumj@<37ZGS;hBaj2eMoNNk_upAXz>SC5G#Pym!sS)5WiJp?CM!+s8r9B<CGwsZ5@kV<Ia}|)+iw{x|36$)KdXRG%u+4j==&Cb_SRPk}pcFPu7Zyzf^x9Zie@H@$z`}4BSn?U^$XFyaP4HoZr6m`$hZgV2={COenTJ<;)~BAETqE-l~t*N}(@gkTn#96D|Bus?m9ckW1+uQXQ45{1-_@!}b9wjV<JE-f)<T0CG0KV+N=;3Lq%#uvcwR$laem9$z8e)!F9AOY#%8DPb~z;DV~y7(<cc<cNSvT5WX7M8IG4llbOKJ4$BUBFL;-?6@BbypLb<rbZG5WTb~q%$UU8Hn3Xk=oY_v*<9a#`SN2Eq0v0Wqp$Gw^MtzU$_Y^g#^b1HABOj^P|i<1>Ib*3zek2CPz*UJHw(T0Ks=Z7#m<K!b}xqdN8SWDN491?%}KeY=xl3}xUUR6qHRk=Ayqtjl%)+UH*`4k+Larg3b)6)yer_jJ$81H2n~2J+VR}@6D|kpZYC&RBW|A328F~q)wxHEEzZ#6_Q47k;}<7%Uu&bE?wkS#UoIcE&+KhpXb+kFW7h|v?OO)cqXZHdXSjC?$uO#(G|n>{=^pDOw08!VW}A_CU;Ic_Z-<zlOSNi;%(U#lj*3!MbyFhKMh&RxuS&G0xD!yt5hAUI<FKPueNOr0;s^yIme3N&F1~6x&F$dfI}Bosy{Ht4SEgubs&!tf79*GJb!1YqxRGZOunh(AUj-ri;93*MzeqDEZ^}o7#RSoA1{A&1h&=Oo=ehlCI{A6hugc9pZps4~^$7?b#+|Yjf~PUqwNcxeH!2DB_y^#DG**EyADp~dld-;r;6H{vu^G(4ZpN3O4uJDN8hV&&X0Fp1#|DfcFIhu=;n<~Mh>peiC@bKOVtU2fZdVZJ_(SzND6<k${nCD~#&aCVQojD-l%TovCP;K>AAL*gP{7p1P4uVwHfToXQ_%y*qO^mke`}Im9p<eJRk#L-Zwid?6=uD=VM_6KZYfqeJp_$JR)#!YQkNgdSXyub8trQA?dK7@Eh}VuOWL*AQHM>Os1ffel{$7<-U7c<9J*EDX$U#7MoEQ}T4Q=V?;<29rV|5_G|SMQIck_vLx@qW6PVW=0bOIu`{`#|fVKsR>Zl#S#aOzYn1K-~)6U0&SCbnbDpj&YR>3+;6G0T~aqEj${IDOKVjRGl4IphXu^zgj944WOoerEd%3b$%#og_>a*d%3lsb?L$@lP<2Fc~zMN~mY>4fxQTq-*vMnJB(Nl-4XLfP&?Ji}8rrz34g{B#sNUB1jft!V0qBeuG}@p2b#W|oBY!0H?o5z|(1rw2*FhZyWC`Wd`52{rj@_|I~4H=|%xz4^&)YhDk8h{v#BjrEx$Y+`NSxku)WG}5+Xfr+0_I4HH}z=RvT+oiu>ovNy}wBK{zm^n}QZNy<n0mCGHAs{_ZRG5z7@BOg%U~p;=cnQYX?r?L<lY~aFbpS_SdqUK(;L~MdV@tImCe-=tj4H}Cqi8yrE#73q>aEMYaStt-S$Mqp`$lc|_y^Q>Wz4I3Nn|Bc)mk~!fFjz(cXWv=blC7j?Z+ps)HF!BAdnZuPm(HQ&`pPd|JVSV$x^exWy&hT_Vw(pd%u{QoNm(giZExA?<-0?;Rb*G=K9QU5T{U1s3#^AjqbYo{g7BD(W^u&a8L;!LZYydLx6fL7AO=AdIyc*t@aQdJT}@gUD&e`1YSl%sHoog^dAL{V4%{#(+EtBvW_2CEwcz5D9XNx0hZm`6>KHr!&wI%d*-PY)JiNEI&Q5v5|aYaG<5<a<#%oG95Pg5H-_{k*EILG*bb$@BuMWhGCh_rPj9p)kQ%mk5CR+}3IU2t+ocg?f}bpC7lJ8Pdxhn@XZ<AH(AQPSO|kZaOpy=3;mb}0&?t*o>C;j5+6?6zF+CNsk@#_Ya@WE6{mp}OnL&7H6tW9MwnP#ebcqLYiSI7`_?OQ=*01WZJjw|<7Jg}=z1M*+QbCm@3fxtaLtPx8JTBv@D&8Z*L*EyNNQdygclrCd{{oDgz1pGsLWiNA_T_u`X!NaDC{*0|6~KuVh9Eo#u74HgPMO$?$66ISZCiOsiFSi}0f;E;B%yFFigZAUiqmWz+vb=z)M)O@RQ(r=Y~JU{ytN5xQD!5hQmzZ4695Q+v~>~z(g`dpTP6Zj1XtrNISeuzrhPGwm$p#Zx9oXT?V%20d}z-Vm97Eyu|Uyco6cJc5<7wkV`W`}PdB*_nr9^iV!(fa4WDoajiW6@H4q;juwNRoG;*1%h`ATQ%1x*V_8KRhmsGI;v4nUqdOIBkgsuiM;>Iw}tx_*DDo27;im}p+b{2UeX<QXW@NU3^YNE1eB`5mL3mx$no!K~!G8?a)u@5)TX@Fm7can27gt!Dlyz-LP;bSOD-iQ9<yR@O<5K|%FEX|O5jr5%{hT&qlMJ`mQ9!SEXk=_USfkx@OV4aS|xiljm-vv(75lVl;spdn+s^rS*q%!bUm%0GmX)-L8yQsL3t!{*iA1=ccm*%a<T@S8!#mYhrI8M>I=lPEGARE0g?WEXP1t-f$2v>+4&%`<$xDZaSu*l28><fwK#r1WcxKIZ4ySy6jEhDD9grDvbgaA)kOJ!MG$hWn9R8YI7Dzo@N|DN4qSt|M#gcO9Sfb*9QK(t_IpPk^^(y&KcAXFUFne@*Nd~QS~X^TDjg%!X|3}>4g^b4j{#QV;*DAi%Q(fd$?CCXwF3!)7|$jQy{Mw4#(1<)>r+*7r)tMjPyRFqJ@wzuvSl%~qp7G)0XUWCm9>h`q^e~(4_?(L1~Xv|>oPo?aHr_}I!ApYr}rCWj!-LZcnw3qaG1=0*f>?VmbcAcO&F6o0>;E{rLuLc{>AY~*%z#9v*EB@F#>}9+ibl?hU2$I2F=z8}&9KK^bmw%cq@pB*m^Zw8(<qW4drm`|e{qpC+RY%8T5AkrBVmDxnUIe?CG^^5DiYoxC-<8#lN=V1&RzgAwgKk6q3uMN%g$!8CTXm+Y8;0<5E%I!%Bqu5y6W%BnNSy;D>?01zr*^WU<@w6F(Pu|x<sCqL<wT~C#xl@r@jcArK7hWNCMXJ{1>kL!c@fU(Q=TcxkT<dYz6Yk6(?Sxv%gK=&%oPLXTHa>MpkM|VHcrhF@Y@*hGBNOo6+MlO;Z|to!Vb@#krt%{C?)SH;lUC(g+UT@m23H0@3(gN8+V(<x1tk3U(Y#NBY7eih1hu(&SBUjf|I%<`hsj=#&r1cpCutNX$Vm{sx)O$H}-#OfFur$8HfZq;;s-@Er9Is=DnOm)$~AotWRl4r{dP2bYU8j{e!u5;y9X<y+hTk(Lst;rh;q4PjO;Oqv~G~um!8Uv&Pzv-9i&${%a?+>eO-yd=@vA4ELdz40|FwZs+pmvK6X1T+uUKa<+^rm9D}{2EwXK)>Lzuz6TgT#<Mo$A1l~n{FB86c%56!r6Re!W>y0CA)EJMMW|6i*n(>E>y$5Yu(mox7%!Ef(BO`m9rKJjLC|KyyoYKTxurAnDU#reH{q;z11h_G_><-gDjst-bHdng>X+S%X1MHdPxEQJ>M|7m9oqnBi*o6jJ>^3%-Rj*wAxhf9VB})>S)sc<6mRmeS^bV3nu);+`SmHvXwuM>dS^eg(bJab_p=NIANR?>{2|(i8EJ=~g(3Ke#k%?6CSop|Qbca%FnNC$0%BoC0?$XRN^}BQYqT-*LLZ`5&YcDnbHg~GVc}uOev)+XcZ-Up+Qs5P7s1*&2!rUdrXi<HVF_=J!#BF?Ei$cLs;AmM;`U(@`bA=`2{el_D?YPUv)0|sY%+2MWAxIH*ZZRp?rWn{C^g{$nf-EKg4Vi<v%zB{#^@zf^L~30UC0iIN^k8VN*;9-3UCcpg^_D>)TCJ*ZB){&)UpLpi;st-^_89QCbFsOvR`Z&6n$Zp4ayu;lFF}8WKR<kpv(1+qn7Qg#N_z_nK-8{f>5`&nVNS5k&3ZKtU=r|DohV&$r^%G<qtmUfvR&d+_18&=;EHuJj2K51}}wpzk{>SkeS3(7V%%{@I0W}kou?^_!K`XPer5=mB6N*QWS@qrzl8sTL#*Xog78}4dXVJ0x)tP6BrLm1SA<o7N|rKwEzlDJOho9Qd4*NJ_O7_O_9z3!{k-G&9>;A80*Wsw`yB?NN<aS;yqrVeoItHOz|@?R@tF0q{y^^Njb86LD%IVF3G-QFbUbR#V}+<6VV{NpbC8}n^+RQsXdvZD=3KBo+-<OH&x8cEcPf2%JbhFIUFNgLH02)(UYH2GsIKS1$!i>?+5~z>WtFBhs97G)<CCPwNDHYN9#;44#O-rr(hL%-Cgk$2NP;qKGP}Tt%s~)@g!1k?|!!ws=g?VAbp@$u0WoJ+Upb%nR3ri3mU}wG65b=KSiH)Po(s@RzFAFXjw<Zhp8%#+pG3uo{NUEZ+};cHDZ5b0?h?jLI)G)N$i@6gLcwzzgtEjC6saBSC>w!mC?da&<&(F#(g8}VjnKEAL=OMI@Z7YxNGXAX1}-*?J0vIn0z9~N8Bpu^377hsoC~HR7t6W(F&!DE_9E+iG<VEF`%HbS~N2FoS~g$PlqX_)!W}yLhTH?aJ4vZ<MgEDsE?t%JI9J9WSM-$d2>8$Bcc&68BQ8zy4ovm@4C)@%7O>#F_@W)k192r=&?|Kdg`-4Q?VguwIMDXaqOiM$UB&{MnPw(MTQ)-PRI3zOzg+7Y&WTi>i2w;5h{<Cj91-ASQY%za+jj%dm1r)g%XNxut$>GsZ?Ft@81=j(M9J4bU^me6>~Q1xG7^A(ixA)+2u=3Nr>IAnIw?HZY4$!o~`YDTRttbpkf=F41OOQH;(9V#|ilT#p=-3r5xdkV3%4MH|^V!EPF3uW3W-cP;740{S>r1l|Ual>9urnv1o=UFWbW;GOV3UG2~xfXZ+KD983!JJxEbvuTN&2{kS?om?!lrE%F#sNOyN@kerK*pUMz<Sm;ykTN~U2aLhmhjM>MdQz*>Y-8@M!s_CU)`=FE=w4jK1<kjT%7*L0G2e01{Nzk*26^Tw-XMA@vE(2|Pz_>uA#{vzts1Llbc?wIkF;UDr(y1I_liaFJdToD$U`x+q+nq#jZojmLFjc5LyOGMC#JPu^k!3#9EERL9+iuWgVEL&P>fDg|8C$aG`w!yaA<;u{#pnUJf)^j38;D8N)qOImQ*Ob0r<2zM?9}=wGRTMz+Es_<ZRjD^EXq|bYRen)vB4AwDytf%LPr8Ls!(^tnla~>R-LHWe(~;+JyBH@OkcDhCZR^}1eR&7V~Y;MO*@R6PwtM-OEew}P!ngU=RkO$e8k~vL?v85_3<A^@Nt=oAWmp6F+Py8@yW}PvKkp<yPqG(@Trc}d=d+{F8bAzJ{DhA(<<o@UFRg)MX&Ge+T~id?+A~JARg)lTR7|npo%b66c2U?F-)R4pLp|a?MgO}_N&Z<egHDhO7>Pa&Y<fabvV)TM>&IAkcKMyg}zP;^X3%H5k7-rg_c6)fsZA`gvlR$;J{uyqLvCD0b~qfo0ZhCG9GccB-r}0?QA_M6L&0S2H!VqohPC|Ko(CHYppLs;|=VNkHdicAZ^e7b`VT{Z8a%yVm(Eu^qLkLr(JwBrY={BKnT}UOigXm=*D%BVY#tZ>455dum0a-U>zB%ezb7G<vKtXhDz&WTP39J2j&c?Cb+sf5<53aKmsRU6wR>5`q3KYv^QiYP7jHoID?1I|8<pcxD)mMEICo4ss2#qn2fhWrbjX2w<t*uY1@kNWu|X<_t6J#h~A&Og9F?+mu1yVWvZ|RcL@C1<T@1|p-59){Giz{oczJCY+GLVs7l`E=Wuc?a$yUmgBF|L2@4*O=xR3U8qkWop?^0d33E}1RV5<T!Y}Pg2;7<5depl~gunt%0TaGQi>gW!*so>v3=B0oCt3pnJW)uL6p9nqDqx@V_rNv%$!udNPZy{~OYO4EwS~`=iFvf1^1!ayr>M<<TS$76oxTWo>|iO2iy5oMfQrRDa*9?}FYmxO@td4CkQ*1<H?tLCRyShBwSgYgTuF%$OOmSTZ_e6&Pj*IdxI@t}Oc~dr%j<3LZlQJUjaZx}(pF!86#y=@87bQ~&$nt;imdjc>7^`97%>l<n`sXWQDu*|>tZI#(cFgQI4ObAROCDtnQtXrJjI(4;Yiv0`DOyg$_A({<qpI9%S^yGW^}&`9^_(+tK@~DhmvGW<Xl{3F&>s)1;PGA3<>Cr7OG_0h(IkTAY*_$jgve}gWBR`kQ&w6k=Rbttt+~r{xHjdY+04Z`RnBT^hMnnZx_Jp2dd0R6#%+mqL!u)+zm1Gi7~B5lh-K^Az^$G8%2+nsCY`;RPE`!ExqHYon%OVZ6GsIgSXdbU5mGe^z9gzgh^$d`~stxj4bP01XAgXl#m7Hfypx$7h|q5`~7hXLazAW_TEriwgFh)cNG|@AUB9;RO)hD@39moGn0p)Dr)GW4eU%Up*~Fo;-brQ^;CcR&KM_;Q0vP`xrGCSL%|C>*3gWCbV;RB#xEn>RvhP5c4(W5K6xFqB8wu=kxk~>kVE;Vx}PlPfDm-$q|4y0LsOD>O@1gP(NCqG+Rhh$i!h2ilP<5%hR5I^<45Do^4dkYYtaqB*kbi;AJKIvsbS_3r!9KX%5o#7j|OhyEg$jC%_&iR-Uw3$*X+4@IT9PR9}oLvj;Qg}D~HDomUE^YhQjU$RD;5$a1u$m-S5_HxYj;37>>3iOSdRfs$@iu^>h!t0cH|2SxyTMs%3=@lRv};zY}Jlf1iV$_Ed#RQ!RN^(`dh+Yaw1t+&sh-B*te1`@5JoF|kl(3*Wj+)(-)?OMuUia|qS@Cg3uf_-PYAkSpLE>uKc5a?mbW?SzbIBt44}1A$4~YE-AE^<+*o8;)5C=vkoBBecSB`H5Gd)huNLgglbk!5M9nj8aT^a=ZKTq#<>KG^(d+TM2)7bK_kkO<qd8hMQb+9}X{m+UL<vp;e)#xe0-vFSSy6A@iQ4eNJZ2IIH5M-t*j1xNs<{v|yBHrtBmyfZ8yPGm+RsFtHK)m5SuZ_K<gaavpk^k$t;nvS40jj<yl^eTARc{=sAVOTb=G-ZahT+&M}wT@9O3F{RZf(`Yuhz6b8BR>)F_pdb(+odUR9?w@@slvs(5x%Q$uDaJdf)*Y%;<Dn}EQ~3L3rK$M)+&A8%GKs^8)tt*T>wTG1DfBPQHn{t_2cvS0keVc2wqlX`l1+u^kxx~c?S3~7+J|W(Zt&J7$l%Wxw)b-OKQMLv#fO~DPaA^PJ|Lw7=YP4Imk}SHxl_<23_q#gzLJ2e$gi%=zWlM}Ea$s~AQYvy?`&t%-Wkglov6%-ny!>48uj^eZd|$zMRQ`_hPe}JLL__w2bN5^nBn~nKqbU)hG^6VuT+_SHT4yFa{3O41U^{>>?-Qy1oT8F49_~&nsYjV$LB!2)d|#%jT>OH%R0veg=&j@y!^SvM*|FiRFlOxZA~!%Q$#K;JpSo&4_dYaT+0-N7R^0VbE8&K)nf<1ak#x;3kl#f<X0XWBDa*+cyW{-0%GI-;x}g}Hp=`Svh2s*+El#lynF|m-H$np<FO5Ba{6|JPWHQMRiu31inBMXSI{>rlhS|s<@+DL`}?<FzWi7U@HW5^-MMO#iuID|%~~?n1U-0AY<@44D25WjzAr3nkl04yxJ}Z7FK5KZhJqU6NXrsoj+}y6{Nr=y$}e`18{c6EK+`tkc<b9XP5SD@lL>TaBrkaJ5z~1YMg4AOXN0T_6y@5ds9KNwxhbs-)a3EMn#)hnA-(uqcEk9;0Vrg%6akk|El3bB@q%n<5SR{hk?S<&ALI49hX;MadVHT(&<ieO<-WDz3OODxAO$vo{{9juDps2^SJZkhORZ_PZ;H9p>x=}FG?+1XF4|(Di6<6Q9O$T-U1v0k#%erFsKhRY#TQ9~{Xqg~E(+G>;$Hu0@*d#roCP^Me5QMlg)&%S5!K1J`{T_6bz)s~1XEX3O9VUW@c|h)|KN8i_=7rqW|&W7qDOT=HHL+?3(Uol*IjuY<*<sD<l=_GbGdNbCJR|}Vq^7*aoNj#y(sxwsf)z%(Csp1K&e)i&?q#p8MjG??A#sYRVnSKt6UTw`c1!-VEq`SEX|_lm$GM56}4oXHyBt|l_B&@G7KYTep&L~N*7)$-w%WyNPKE4N8KV5%9O?h@Es-;dDKagf!g^tdse>3`)8aDei`L@eWRUM;j%D7mLbG#TE^=%$N|1jk(tXi8yz8Jc(2GCK?9D?9OwIYOenDU4G#4iRP_e&hG*&3#EvB&Ph}IM`L8mMai|ce;VEuR_t6+{QOfr<F^!lM4Xb}5&crpW@dtpvrTeLmzu#>B*Z-oCJN*Dhfo4CZR0)xCGI$gPV`cWu5AA^cx3Bs9*YE%G`FGp=a(b;zU;X;$KR-SF=&_%@SB8K4s=88p^=Zl-y?yXyC>i{jp7m0&{q-Y%`=!V|h7N*@hi$&4e8IQ!OYwf1qv!mmNk-pKn?u%uzIZ$DDKPCXPd|M5t1yx6eDMh0@M$mKmi%V3I@OTwQdXg8O5$nAobuEsj1VdN=y`yxTCXVTU8$`2`CX%K;&9Q0KCv^g@k0ew0IcxU7n$?V1@Rg8yvnghZfg@pz9M{2obSbBU#I!lm}Xk<yjA-3)BAG%Tk}4o>=z}C8%(_6m&1J58*MknZj{m8Z9-u|P0@(Pgr2|KnNV>hEludn#q4UBQtAtN9j*<WBJwuYH%x5%6u%nW*r|+r3vZJ3r>!(`715#Z@CrXZ=SBJ5Gtl4&BTCEymt!XlRcmX-kSp^7fo%oeltcV&faz}37+f@3(i_j|Fo#=TbDLr2o!qnWmhwnTqun;M%*NPA-z|@rhz|z0%hKBHeAAWX*8h}4>E8BNtOefT-i3z5`xf&l6P_6gw6UKfaTZISE_mLgw20qV+67GTX&|6V(>rPlv}bctK^AV}+Gs6vJuNT_tmT{R$;`nuJvWhXr?!CDUE@#?002MuvZi|vDL;E1NQ!OJJg{iq!s*>G*JRFAskXKGN>zBc)5@iJU*bz@+$6B_%>>Wj6mmWM!o2KjtP@N?hTq*Qg>aLMM8h>X?m)KHD3Vw|&8VaMqEtoSE@c0^&*~E4?erW3Sd~4#Lk8~}&NS>WIyo9&yWcSkgG>cB$<mI`%Uv3K=!+6bKj?<0V&lUC9zzff&o}o*%x0_G`6aSR#4(wM%g6>=UxMCuLnB|)5jy&hqJu+vM90h{T6ZjS)Ozpz3x7QIJo?Zf*ckC~z6U{GSd<72u#58h?X?kIN=cDx@!A(&oAIED8<$~K+HT#$+^uU=a`s9sIqDb#`(N?0M$Q$9*PcoR<wJ*WeV;T5>D@19NetBT5NeeY;I&*3B;uN9UF>=zYc5o<taX33E4beCA-JC;MHtkT7>GS`wTwN2F_8-ZD-kd9VPE^XT1i!8MN@K4(6|RnHWW&1%vV??`Wk5-r}j$U=MKD|gm1hBWGPecaq<%IoD9$3i~t_y*(}b3u9eBBkH34~-5DFm%PIe&T{C2o`&nMi5THUj${q7+wSP85P1&?zji-3*K%R2aWCd>F64C-}8sJ(dp{u^#Of3<sluLY-I&fDkk6l<*;Ml(SHu$xtQHqBfg*{9Fx+j@5^GZ$N0h~tbBz=f=mUsh_8z(Ut<7yMUz=>USinYx_2zRv{&LEjG5;qz=$7N|4d^HgrHO8zIe{?-sI*v~@(e3ru_#RetAD5P57htx<@$>4*e3SNm?@Yhzs2x{pwIX(OzFjit_Xo_1`Y9;|na*X0oktF-Oq26N_(l5+LPS|Qh!-vsj9`bfX(alS{!gvt<BZZ!%y{pk{q?T+?kl^gHcs&ST9U*BCIxHg2lUqlF40<<WBYA6ua4g`VBO--xmz{=8$8!lJ^9ibn6hg!>1*r|m<bF(TW+CECK{kO{j?)h+^S83?2;xWk~Q}bgud;?u(xIst^7&hgZe#oI9louwq0$9fZRWWkV6L!ytw?4PNWgiy6JAxGifX_7SI<<DzM9g%+C3Q(+h18A51b6rQwL@(4-Y`s>`K5x`0!)bh03qcG-Jrj<Uyfoe2*S!aKn{HFyT&9RPL^&9cPMENtpwu(tnd&IYo$l4h^(dL+40IB@+mGqNxr@3j|W*g5@%^5Se_i`7q2F0Op4m5Yzx8ylfFxAh)bdU#0HHH~3Hyj2Rko?USn4y)Iuz1Y3&P)Sz)AhM?AD7+CPfPUK&eGq7HvWU@AyS~1mIyA`!W=ct{!j$>p0fwk`Ydp|82gfrDnmHR#>^mGkhWyCpJ?ZqhxRVpBE=xDorLfcD79xg4ka#9Gjq1M9{Yn{yMEXXJCP=}mG|l;^P<tFX)!}$}TTNHvv&Op23RXg7g|dT{(>l)BK<NpC4>iU;9B1)$T!poK=cSc0NTSL#!6rMs8|Tms<HAw+w=+`R36*a2$XVSlL5O{vQHWmqb1Na5tVW40&0dQAH|>>4IglhBC3YdDbt)Y@kH6?z-|w*sl)}fQ&R@69;8g<UkWO0_QKh10mCr<6qUR~g!>Oz~2IvD+s*dUZRML5deNgvUpts%>#$I+{E|b<8Ng?!pa^?311ns-PY?6x)qYC^_6{hULW8J~*1+nm0EVG48O?W=eKeWywLx0GgB&)U6#T>FMXOTHYB&DomDwDZ~+(Q~HYI_iAkg3=gs-(E`K~%%FBZ6jm)Q?Go+A8b76}-VX(9@HlX0KX<6yT+Zu`-_Fx*vc9nNFZX)i}JS21y&6fz2SkBtoV>+FIq-in2CO%#0@56Hg`v+N{7v`k^CPhnDm&mK!IAH|dZv!`FD(S%t^)@$`NET;v_ro5itfqDH_1QwiaDrpD20X3xj@>3K{9BtWox$y};f<*r>t++dm0Na>+XdsD^xEif&isQ~LLVtgSeP~$^B=b$bJavOEbjIO^I2<Lqd&Q)Te@<Cdqq_;s$D_>mhpd+#9e|B7E%l{Ke8BWk{m#fgO;E9Bab}C_AfpKkx7Q42sW~+fTOdHsCX>Y<cHA`FmxV%oocxd6Ls1I(`j%ZoTkddTsG#BxTUP8=A>>~0oXhRjANbVks_OUrD1_oMUR#opBlsguf$V3i7*c$dVEU}e|H}%oLFeiJOJ;m!R;a+r{j>5dk%*FNR=#Yq4+9M`?DidcP+)84jd|MK)ksP-z@R$<C_9Nm3{?+9UL~C>j<(9Za67~ykDqX<tLt~7loh==4MFn-Q*l{n)42!41=k!|8>#>G0i*6^mQ3CC>W1v{V83`7#oOP3DSQm#4_j*%ZALS)&s92SArfPhz^EMUu7Q?FL*|C~k#&P5?+F56*y^g_XGe!S~Hh2-3d#r}b0~4Q%2sAOn8nW;{BsXzM1u!wR_=75l6~OAtQEnE9->NZo^(-}1s^`gZN|4UBjzzC=cgU23EsT&D+sP?T>WP2@nwQgi!(e|06N2oBBL}R4e#J;iD?To6g!dWo@^|&S-%UVZIf6L612x1%&~(*GL12V(XA+=H=(IiMd?Yj*qXVbjppVu%p$BA8G!!%wE!0q|%z1^2OGzD4^^~gU7pX+U<^chXEzoY>W|&I<aSp)a1E@9%;3n)~mwFmfp6EFIcspksBQL^F_@#uo1kBdksG$lr#!Te6I3nDV_8Ofq5#Sg7BfjC%UXmHM2r8?VI_|^*-{Y6Ksd0n>80m2nGbC}J4Qv)WxW%ttw$`^_zWmrkWHit3=p%gnJfW((az0c+@i;2dhv7Y#?pw^mr2g}RTgBfapA-m%988;q)qfyXOZj4N2O@SVhFVA7@Ha=XX8p@aX{P96YZA7v3_K!hOY|UBH+uA>4cs<#GxS=M8~zEm!nzzQ;IBP)_K*k&cre=Cyw=Gu*-m#eK=BfB>y#EK#LTIpJ>q6@h8{N$)~Xn(I3f008~t?O6o~h7`LI!DZ}UQX$m}2cI|x_bGO!-`k3ciSty74DQJti5n%S84SP`MUGq^I_+{61KMXJg=#Q9v5RXb#+S_gJi6s4+r5;-+$=uCfAqBX^xfO?G(V>R4{9j)qf${ZI*D6p@Di$EUnRm*8^2M@_%P+;sunn(;XMe|av=u$NkxwNh$lahsuJb!=<Cy4YasMiPAnmGPNf<bvxKK?7FhITWc=$%H4na?oKjb_uy&(nQXRtB<C9+aq0HSjR*iM6mgjlr&s+E%ww>8Hm(0QsX)354$8#Lb#u^)=Z3G3<%WU=DWMy@YQ7aR1RzzEm@Foy0gc01J6}8nO$=F4;nKEY3$+0c;f0E8cdyf;h(?s@Fk5m5}6@_Iov+<3ND&^$(|1%%wL$@<RJ4Sz<2&rY>%xG}X63Gcupb8#orF9Yp<Glh*1mZ(69rHNbXLV1%zQ>(UKVinnu1o6_kPXe6>SjPa6={6MhMf)LPXS7UEKkJxQaA=_J0sm0zoY}Z6Jcu$kmvBUBf_?^tqt^ZC#$cZ&d(wo#8)8ly;$v`ok7?7k{hW5-+Ym^#7jB1_0yk-OF8e85uKU4j)ElAWx?Eo&u()Gj)j7XVwJ{G*1-1t!Gk1g^C)>)bepIDDuU%cXn{eTqX0M=~vXv>E6kQL=H2|4Wa+N4qLy0<ItZqJo#3}v9nfviWqhqp9HF6S;{3Obr5qy*!V))55)vcgS*a&Z;P#tvc>p1L_55j$d{qu}ZCWd^!LQ%4-})b)**yKpnJB&-Kk=ctI7HhnwYMhZN{FjvvR;H62ZomYc@mfN@)|ElWEPi_PAdLTrMh5c%*&k<o$X#37Ra%`lLwjB#h{CvVesXYfK++f%){r&1xRZXP*?)t{ec@l3Uwn7RRCg}?S>3O2UbcB8Hhq?!YQ+vQmFvd2An_HfwE`qHC2>RL+qE-c;7!%uBstqwA$!BL&k*gU+)5&b{CL307U6ze|Xur(D<IUeUYP-ijptdVxUe!e+E19a+%Ap1n(JsEDOG%-_h9_z?K5?a{LB9ooyeNK>C>eupI$Zn52G~rNnguRXRuQ(ZXZP3p#oXj{leSlcIg@-}QQ`?V`0F><XMTesg>phY*`R22*VXTb#4?FUC0c=lO85{Gg^e5n)MK$gp$N}AXasMyhv?w3(U$4Lo{b>zG8#ff>dvSCC};!&l?I+hU}}_g{IF`7Mc_bD_Du}1?9i@YD;e|6I_TIlPqm;{V!=>sYsHb66o{s&6BsFzYkTLAp%RZVq&K;yxwpl3XapufdMA<T@p*a5qBT|2u)Tv2;3!52P-NOJjUW^JWI?wOOtIQ4EYv;gC*g*^t`=^JwI5`Pd;kt#b|QdA0mMp)j;hyYDBp<bsgR8nkK2>G4$kjy9-PYz!b78wT_Cb0lGq?dJdjI#cj?E!eEzY1Rgce6PROzFOAD2~4t$Xcsw76>u96(;;sE7w8BbO59vL3`zBoiW)b_p0-_QLQVBGB04&4_z43)Dl-@8YcZ@ogH*T$~^POLBl;W=>qt1x%U#9lnss?cfM%1cVL8`KLxL|G>Zg>zA)14>k!=IYos$Go9Nb6=+FzgXn$K1b%QO;F1(8!44?T@alBKmeqwlL(MbU|HERQJo^V8gI#Akl8Tpi+Q}Xh04BV&!cJ&br9o2d#*@x4X}>|iWb{+-dd2@5lk3s=n{Oo$$ii~D=82I{tImQgga;)Z6T_GnDBt{(h#7L%Ungwy#Q8jLQSpLIO)8kiUo)z#Dme>=`bL4)s7K2hH-9{dYO?p5~Na$m1eZF$P@A6swjeY10GZpJw+=y(QjVp$h_#x#&ML{c;$(GxOq+k{6f2voTDMcB^WZ5m$VKaLs9ZR^dH})4Go8w3i)PfhSY1M?~E}F7t1Yjp*r<IVik?_J_rpoO5X+3bS%!L8Tt4waGH)#`V&qyA39bgS5_yLfw#KU1?WzbVX53j#f5BjBV7D&8LqfAZ#}kpaK$TD7HYt8iq1XHcclE-=#6P7#m0I!Sw=#*LgaWR*5SZ~aC(JBUKVCw^hGbOulvM>GN9k()p&0iG36!vbeA9mc+#pV%PK;?t?i?C+BH>~#RuZ|>=w&X(YGL^AWQ|EzjOei1v~rf1lN{^J=#*B;+W1ves<t<BPvN-*3mDl0A^x1+uWdEFs&lqcdk0A4%3ashZ-zV7Lza#Z4g3EZiY9Sbki?@b}{6hs-0b(N1dmlgvPbKb*G>-Rlc?;b71!(Y#vazuVwgqEYf#xZ%jvH28(|x1t&a>hTjA6Pya045`^fE{S%?Rq|YmmW+-AeNu06k1jTVl3Dg3Q6s&tS*mwphBMAcDSeRY$$L3)#<L#gWS4cyU;O#=!yXWEX9pkzD(`<>K0|A)#hgK<PIK?rQl{xB{KNqe#Iv#t-gv%7W0b}$c*u|t-mDW;R0a*R6taemFIzG1&5>f(m8}eTuGp;RUz+&F2GgaL%gqLfPXQL%KQQ?^IM!7)h93WXAaY#P3lNBw`SI&(-J1Q&h0OBhrGKDmjfnJO6VIKDZ^vyIuQ5Y=%Z>!9Ua894{Oi_lsiS742FwLA6lGt5Nj?iGP7%*4uHd_V-Gr+KMYL<ZC#(<ZJfk&+9X>1I)LNgb3c=n96C?!BCc~1!smcS_tlAx<x%h!6pwZq@I+bq5nodEiJ&dD0d6Tv9N&a-e1!zK}&)E&_mWCJs%!;k+g35iKVh{{o=DT}(X|5F1bacImyB*+nWg|KP?WQRBJ<s_=62jXLWN=rHww+5vP(~#^R%%u~@(VXlZs%DK2Qmir+TqAyp6H^*h|B8SuSmm8H)^_X`nh^6}JE2vlmQ&!fxT$2g54~jA6WMV)mp7NKP0itop6QaaWmKtj6;?73R$a2Dn#=S(!1ytqwITml!5-tEEH1$7++r>j$>lY(61Wf9ybmivjS|8ZRFhw)e365-)gi)osSJe%chu~dXVeLTHXG(WRLjUMotaOO1Yf)fXT2Lx+2zBZG-pupn6sG^#)ebB>|Qj(Wrus3Puo?Oq44k61~^-kOV{ivAA;#t@Ae5%(iR3I7sJmA-R+@xlaI~nckIwi3|`2uPf<pbhNjdz`<acNwnV?5WhnT#PyXc((MHTjJNzsR!AC6C%?CFTbJ>(4ax;g?`@0Yj3o{aUK4Mj(6UbVljhPqv5VdmdG@zIp#sLir4@35oq=Ua(R4mml76-Zr*3Ll~M3*%UIb{k<cyk=S(OqwmY3))y)%Fp$50lU@5^GJMS&UinnYEg=?rvt2kt-OZmxjFFAB}Kd8=XR_2@lBZm-`a5)>WJh9vd-6FQJ<E+mq-*c0g2mYZp=SsH0GTYp^PeT$`gN&FW~Ql5VAzEr?otJS45J?1VRwO;wluV#}cD3#)8U=Ae>PeuW}?nveipu6G=@Y-c4V&kxANIc*Vyy1mWRyd#KIj5T5n;+9cidN@ng5Tq)9@KFy`os;2)m1RX2_iW}FK0Y^iDa897oPCDOB&M>6|4N7F0o8`oN7cZm_)&Q(B8{j7Htm$6INUr%L7Lk#(0=UXDDrO@x3Ls}k^7jycvvDJ$uP1&C5os8P-x;AXpEGay36+=U<PW6bOsnEui|aCMd!p=U*5e{+sZ?FTO1Vc@dEW*qC#SdpMkN;4s{_#rVUKWk=+ZrE(dW*_8o&s$d)aJAtRcI2H^!&=v&#ulJHIK$rN2dLCp3{Sth)xVrFKsM`2K&|K7;q7~u-CkAaDv{FIs@o`NpeBQbqP5WrMtlm<R5hU%~eI@PLuVu(0eXL@lMX1O^9tH|r_ik~=`P}B06P6=;4WEG1ik%D{oyQNU|MQH@-1HEzu@+{O|r-;audxl!jAl8=&@NoJm`mB2*rO&ncIpRjkIwC$yRdL*2wI}mjG?ab&yHczX`x_HzF2E8xm^e>j*Hj#|lZN}<G72f7jQhU2bXu*97Jh<mAiXi}8(A0oaGCv3M;X_#{@ur2Q!h39#f@lB85F_f6FENOR!Ns{mJ&|Qwhy98N*#<=C|z`+d-P2toVJbu1(nsJk-_H-?Ie3TOd+k_{;m>gXV8VK#d#a2CnZOH4CUQ9Rx}~Y<SWjb<6#>Sjd;m$(lFE2UU_@hb@o#hJW!9p%v^j_so6x2h4Rx=p9PwV4LPd~ap8z#FO@*v!K5_`I!i4w<e+srt~X?2KZa$yNljG0=bMaBd9-A_>PEt<;Fp%W6iwgLi0LboP;`SmlGIM6>e_z)uIP*|IxnCDvX8Eqvth?g8Pkx?ctp-FUusH1?0(H8ffRNtF?#T9ZSULiX_*BT+t_6A``EZ~M29<0!0#_shqf-|2v-EV)XKPN-<D+AdkGtZjRJ;ZbEEF3pw+1a`p`+QrIU+AGemjW9ww1t?PQ7}|MEKHpZ?=uQmF4iiV}N$GUM#W)d|8psaI){$CyI8yIX_gTx9%IhRDN0pK{;Y;3j}$1{z?@J|3MyVb1R6NrF*LFa6pFrOcoOMZ_boCb!3cI;=Z*{f0<_o=vPsbkaKGyPI(tXww761u8ujXsAVf;DyaoSfY)IV&0KX<p`VPR&CO2`x^vXdLG;EBzklEr9FhHLgm?wRQ4p!J?xAu^O<I;m`mMugC+yZPpwerhRn~{l11Nt5C;#59)c@I55N_?`1ssFOroytlTn>=3+6kWydGeu)<=;+Mtsn&Iy7%X53y!Zu5wXZ-jI(Cra(|x)i4!05};9qx+B(%Ilr{(M8)=tcaQ9es-j@}q6IMtHF_toOluumbQo^hVcdLjcYI!=@mPSGI72-L!u#YS4qqcG;rgkM|2Tq=%UlF;LVJnvfs~C;UXGO2$QaxG{6L0Jb)@E#Sh#i3ub%X=__CT-Nr&h<C($l?eQ(z;*Rp*_cw7YWP&e4ZVK)F(gsGx<utSJp63zL<n{R7ZvU#*$WhV3kka<?Jx4Ll#UH7QNiIzXg8Qg+2RM9W=by}D=r(llo85AqD6e<sVEFmUL{^$b-_Tmw>RQL!WV-VY{q=uF8h|49x)|YK(>q(ioV<|KEzG3S;5d{LWc(Pb)eHj{WV0U~R2IL26d-k`3VDf9LNr4mVDMF>!w9q*1;-fKjxk>~=xSnEaYMVwku7eEAjkQV#ROfs3{~iPD$WZm8g$pj%0kSYuS|8ggA#Fb}XE-&%)zy*MxlsZVIQgPzhCSAg)+ndFAv<w;NCd?hJaqoAtAxXysP|{di4slqhbqTpyd5$<iV?p>NqR`zR*Ww*eZ#wtK5#?y{@fiL;KsQut7a-wg)O*4;Lj%4sqhFzn&RRI&3@tJ4~Avi^1??|@-{z*lVgz!TQD88*!)gd@PI^Dvq{&0R^$!+yCF%Ki$bg_5vdk_X;(tv&fM0c-c2F|7I+Gn@I6{oRhqzlEvsi>sL?sm8W7-#LZYNloVZp2`=q}IuIW!^8$)@zKrLEomu0Rke5OpyqxF;rcFjITZ3f&z(v$4;MZjYROIcjZSS<!rEas6@w5ob}2gZrt<h+60xY)j#tq8Na5i70@^q}TSN{m>NR84<#*7kd{GlIh%iiTmzxE5VrZ+mwOt!r<@;xv)A`ueK?aG}je*|vGURkKoLwHHk<Wog2QdDz@cdtitvd$e5_Gf|G_HYCSM35=#9=efvyE8*fP-i!!G%HGd66F62jKy4{^7~WrI0=_Y$`(5xL7h7B<FAP1DBx54y;wp>ru=FYj_9tRUKxed2CDTR(YB>QJ1LSF(<XIZj7AJ$$sMe0ecA9Qo(GB&7Sq@~&syxnLC+DXx>dtt(0A4>(Wj?9^&;=8<G=1Q1h@nr6X+4^}PI(9k<BQlRdbC8vQ{tv-Pv>pv9Y^gXL;7n2nTZ;_y*}$&ygj6E$G9X+D)ZzQ7{z2{S>Ga%N?)XeEHDpDp1HUfbB)>Wk6RFO#Rs?dhT5_X!1BJUz(57LK}4fcm)m-er8t?HJOouyLl<peXKD%cX(|vGU7o9_`rCKLIC+FxUq;F;93UJDUf8jQW)!4LDwQ&R8R53#IIprp+f?+)>!1}`6nTzpGS`M2$~V>hWH|?fperX`26r8rlDup3Ln(=VD)rQMzW7^&QQVnyd3`oK2LBj88gG`@F3MetZUDv>t7rR&u0u%;GmkiJ(Ti4=8!>$}a1(F&h;MFAiR$x4m@>F#&&|t`*r5G**e7#Dji+8YJZ`X@GvzQ8c1NHZ6fT96NXqSgw`Rk&_Nl>ev?W=(MVV41BYLc-d*}@?lbFeJT5wP;D{PqjAvXA(Fa!Pj9PG5GDpZ<k$)lP^`~6%C@nYiUA*LWPJ|o!Q#k`4$g(_S4)?KoG2+&;ue1@DusNOdLm(j#eoA`lT0q0mxBUhG#cFAfdWJDwBS&SG6OxjkXIz6o?bE4UB%t}Dd0+k-26^6@Cyb7&mDH|Z<k<<>(Xq#k|V#1T#-Ipf~sT-tGJyqLE_`{nU?;>gPQsOn-<dXYvc=6LdkA4cR3N_752>g7hmC6g5_blymGJD2Z6({wc=Z?aKLs6v#qdYTZCwT$XhH0FM#2$i)jo7bLBuBP~ywj8O(8G-E+clE~^D=X^jkxbC{KWPT9@Ad}_JZ=JX*TE1QF`fW*p!MXtv;DXv%&Q}a9_1TmO=ytfdJ_gz}<5H>{Fq{N_5P%7u88I-a)nQP^B6VT|t<_-!Cgo#oy<?@g9{)97e3>T&7v?%bZG~e_^)4-OoK3m1~65B<Zphi`18FDnyTbs?u!tyK&GyOcQZ~w>Cirf4;E2m$UzYsq-&B<ZOQ05VZCIDIGZf%iX+;`0&h~f+k`3N&WVf1YAXab#3<Lk1c08-z5a0D7}4WJCpX#ShnayWlq#|r8Lo~&!2PS(rqZ36Z1CAolp}Z;S)HpWXi=1?{@$yA$~JNqc(V@%Ji$LugH_rcR(cY$tqx1Q70#$Cpuwx*0I){(+NC22jZ<xpl)p30FzzTIW8zvTjb;A&n-S0U;w0=EXHYTiUF7+a%ti5PnUbpvL)bJrYN*%?wOh!wTh}9I{=Qu?FCy%0H-0p^4Ji$rM$+Aqx29E8}}E#IXkgY=J$|gKknA1;%(>UJJ9TY%wZglZ9tRLw<C12-&Lz3<@;8gy;;42zFC=+{?jkt|M1=4zy0#%$5Mc|0gmX-Rg+Y#mrQTglCdV}!GmJ+d!a-zlnC~HVPS*BHVVgWk{*0HBR)11)DTBnmI!m?6vW~mpF3B6v4h<B4m$vvwi(A;-?nMeS0|oKphF{h!HbWW&dVt3cQZR9WM!Zz*FHtndgRYdX=R`$kN?$Neu56^#pkjc#{UgKA)BQLxP)p!f`Ew^WJ80%bfAk|rz!s!uh%_1=o8lC`@Di)a2YH2trb_u@pu6#unF|{mq1am+LXDX)_YlMO|yMd%%xsuB#@-RjKOo!77I;0v6$jON6qXyqfs<g<6%N2b}=lzNE+-95<qiNur?R>`cISh0B`3k$l2jD-GeNY!3vA0PQKkAZyu-<>!Kr=x}sVl*inxU$iVprze~X%)af(Bd>RuysspMqEUaB%E{?qJ%JV3PRkS1*Hw>Q3h2u6^$eI%yt51x}UheBf$=6C<B#wt}mnj2EwX%dpp@Ge~O*&-f?kKNHX+K@%qVUjf`lSTx$0%iK7Cpa|J)5eiCF8uoz^bYYp=Xj|7%}t9lJ{1+@LKtPAoM`uQ&TzW7MW0{G%kSeFrmn!PLd4N&bQgK@;%-^<81KDDA(&7?Ys(?g%Pq0A#T$$UZ+70@O_HRT&~&Z2qD9JMcxP+aCGK4-@ju*fyHldsNbNfH;6YpORpw&EctjUn;6Z1m3fRqg+L8YabvoV#(0ZTzORXC#H46g{S$E}u3?Qo0Q@c8PksFTX7j)P7meKM2RI5e`!S_Th?JATqbL|Fvu}QA2kgIn&F8;<|Ci6d+vb<kYi;`K*FXRH>FGz0{p`Im{M%R6mD;OMQ|{>PgD*qL;Lr4|mxArDANkuaMeZ?l5L`TL^DX5IzLj5!_tP9b=RZv{`hMCRvKI8k+j&ocX@7b8;mcoziEQVKNAQMEd-=BHH=EU|hIE&*3Pn>APebOEr#@kXNZCiv18miLMN#icWyR0$8g&zgi!Stuor#SfDyRZrg|EKIoPREe&$#DRjy-Z)n=tYf;d|nIFCP0k&Bw+x(|YHv(yyQ1m-FA6_aSA!C~4ea;tjtX=DXf#yD@g7jP7m|3JYqAMl>e${N2ukiYsYpLT@f+SHqN2U&!llZQvA<x3RuqV%w+q)!@cXW!zhMldL~&rHQME4t<AL`0+U}%I}_m21giCVivd@J87s|TPucKnHLCbEAXZq;%@^?ccaGOqS2Dxcut2o-1?f^3^VWKo{hJZM_L-~wwYx%#zy*XdBj9~Ft}Zo)@J9Mt}M6yryNT6w!dO6@DBGbG$h`)m`|DT%ut|>{Tzw2Sn_ni^CqQ5{JzpIV1iEr0acpbQCpxro0AH%a1+-?Ynkh5fl**B-(*i_4zB6BiG(|~1;p+ehk^hA_`#Po-Fry++3P@3Y?J1JMe`O;?}oW1bEZnQt<6`e!o!_bF3tNAUsB^Hft7D2cm}7C>){vXWnW{RU;;Ay?p`T`n`9&!uE}u+vaLpu#QJGQ9o-kDD*ARI``>+5mk4jC=ODnU?C~8kc-L^IVTaMl(fHc^j$s&NDzHhGc6?s$(%3^^lt}tPH#8L+9~ST!f@pZYxi?}qTiwntkxe3w$uwL>HqiPK^u8M!`I?T<(SH;j9MU5?W**VHW0|AYd+%TP<EiJ-hYrEUh>!C<2=c<BL}-9rl;3Z!jp$NJid>7=zVO<N2Tk0#46D+1>mKHAU89n-S8B;o#~9fEikCHVu1LK0R4OPRI(+N<q)ABcemP5Gpq7VFtCRq*<$@p)*F5WD*Be=Lp@L<t`?Foa^_~yG{Uj;EpsvI~?2)Tw>=BHKTmV>!c##kL+RxQWsv;|zl5>K_Jy^1#P-0`g!Ya|%Nb@+gSNcA8;Qb_g<1HXdnR<_tmw@MFc>ZPt@G#G2aUOK7Og?@5-Sh6w*g#%R`4{b)A(PzC@@j?v71B}em{+U)vmt8ArVVR6#bXEZl#?baa0{1^7GTo=*E$JZ_3dVAiCCpv;;YnwyJC6l!m0wt_QkisuRV=YJlrVkVFJ)S$)uTAY61`7G+HO=L#(sJ8<5;MiOCpOo8Sdb?4nbwZ4N@XtL1P8$&`_}(cn2QOT*x+iRh>?W~KO}>(SD2e5#3VufN9ku%i38v=qAlvn`IFS5M}fwD)^w`dvruxLT_fv7__tl0m;eU{=&mNh!#5E<5Zza!6&GoFBq3+Gh|V%F;o+aG78PJETn`(Vz5xYAqjUl!ju)dmrtucg1&K*-f=^g5TGYBqlH^SVKRczcz4**2)~)Z_9ag{FVXh7KhH=s`=mGxvuKTm)^jXU6V;)V~4;@U;x^33vDvd0KMs_9jW40Z5m{kG%1m+xrZS1Z7+tsHIr!NPYNH@@3F(tQirhZYC8nv{uzWEI&k2{<&ShCjgZz&caxq;V~MeVzF1O$T^?k1&L^B+Xp8t@l9?zCM?8lnt$<TqF7?p`oT{ah1-Z1#-b-_oJ+A9ac!&_*3FfK6GZ^mxu!CrpC5C2UQxAi+{a14~kj0fWdwtg<$(6!^>!+EKh52}|y%@vJ={J-YXA@hjeu{E&<x{O(eEi<n2)((j_sG)2L#nQ63=`t5QsDLMipy|Vy*BN|?rn!kvhoL!H7!TsjTiy++m`5qK!cM-jF#H<^$pdbNj5N3N@5kJ%nuJRM6Fxnfz~-Vo>|b$*??l-;rKD+M>g+Cr_aTmoLF^Py0I>WoffwcF)V__GqGt@_l@pX$|xk#H)=FN3Rb0Q&Oe3P<H)HF$HUudx*DG~)@4?(5+W;<9ju(zamEHpPZ)ftG4A0wi?8D<tmQi|t&~9$Ri+6x+3DRlhi(`bj>5m4k?KyUbfZVk>V64A?Bk3=^xB_W3DIOVN_1)VQtZEJuT08;B<U!z3n{Hr>DYPvMc4X%k5!-)J}!0sx@`up5-5js+Ny{u6*a4TCgKu3Pgx#LWz{i2AD~ioO#i2n&NJ+Ty2k>&^`<cPvIBFOwAM%pq4$$3zc(Og-vwrqTznW+;D4$xWe*<f4rVWig~wu<Eo^GS^Kt&6bru==L-r(Dt*tKRkYzcG%qb!%WhGOY%su2D(qK{BgGhr+#lBD_#gz}D8m=7?G|QuYOd`})SqHA*4aR|<o(wg6)f%J#FGY-%@eJ4f03^tC0v)Qx;Waf#+Sm+i2Js~kGWF5cDz{dYwRvJ@G|`@TGBMC*1vb(T9mzVhq<^v8I5E6Qhm;w<#>>tsJeH5A@AKy(@37u1j$IQq0v4D`2+uP$j$Si+KF&|iV<I2{g568zQpGBF?JD91%bZ3^4{h3;D&B8_X$egQSXU9_3qgSzAM!Z|bvcmRsAFby{k=dq?|X2r5(||N(kdmr4Qg8X;&KNaiADdj<1$<RpGeAZf_A%Hg?0r`BviCh3F``sYb&(awQV(94Wwb(z_v?!6RxRQ+VaQcbsEM)3qM7DaHDoa%VLI%Bz>c~h*$IyVm@LQk%vJWs_;Z|_gJ)#%~>%p&=Rw%de@-bvA{$oatOlKu&-f>txUYBj|PT0+0*PPUS|pSqT_TF=2d1cu0KbIM7+`-G3is8IQ!sM5*y{)l6Z~exNU*Qlqj|z5jXI!E_WbWqf02a#3hojUwBjL0(Ku7V>In->4+;TsC&hZdr@XsJPkgl*MeS;HH=wwJIRd_Xr~<m#S+d)u!!ZXn>@q1IBdAro9g-~FKI)?s+==b<9nUAslc}wRxQtt)$B5kBY)A(I!o<!3`UzN`Zu(}i@@AtHC!H;_*_Jwi5b?Ah4&%3iAySgiJ`?GR6(o&R$q>Cvq1b-jj^j|si9ImPmWW9bhdRYdW}0@B3Pq@#OO{=c~VaW9MQa>-a7^hJlGjv5=g!%wLV!ZF8)&efw&po=f%t8)iZE60fXg8;_wdC7;}F6((f1Tvx7ZK&@!Re_LMV|(0q)Jo_ec3S}TRVkU`c^5Kgr4L#amR6+$khcSv<qs`6hX6%E@5q%^jWyLrQ5Dgwya0FN1<+9-gau)|)pK_Pd4{&;+acvokeBQMEM*rtTZ0D=puVq*+Nj*}w-E@`#VDH8#I(NE%=FYPFqaf=|cYO&*fEbu;l$(tHU7?6=3Ix%AsciX^fv7=l3>Sc3%`{m1zO@v1C6py~b*UuB`sw*c%6&R1BqJ0?NgV|9Q^D?PF{oq#h_sA~=f*}XvW?}aqh~-kg*jpzQb}ok6N8SK9N3~}C%t@)H=xS>cxUUR6B5g}FAyqqibfpa(H*`1jT9q4K3b)3(oGak9J$Ckx2n%>H+UdO3%`n+dcQZio5^?L47AVBcslq+tYH@}hHxJgX7`Zqh`dS<Pbl(&R_;UHMab|DxLVL*UANxHBXWufg9vP58H^Z${h=ozzq;Z<r824Bqp}jM>GTU6l`yxlGN;^dRT%=VyWTs*Vc2pFps(TVSHfktMe^sJ2#hrlqjSyos+=d;k>T}8@7e^?tu!NI9Uh!4SX>JD(*<ny(>_wtTj50+tQ?2k)H5a)wuOpL^WsN+4fDI^!{3@u}2iKZ7{zZa8c~d?fET)EbGoa|5M$DPdIM0n|)5*`%eN|QlvQi$js82ocFz%7Huse;xu8rDOyHV+<$3FlGq)`fl_Ta?Lnt=5+`2I2MiOpaRb{oEga{!S4(NMxvGjpB9I5q$bd9fO@3&$?`LUb(7M_B=M6w@o-cDsT&#~-TKL4lQ!<d^n)HJ;-@kn;5pr_{`)H$iek`zTvtZvv(+ZlXNZw?Q*9pUNFL7Ns3T{acgf>M(C&sKPbCdQ)J8uQ2P{4O5D@b4#nz=^kh#vNFu^lCJzfz|sN|&}dg<Z$FRNZB`-MTT-pXUOH^wM0I#iqtvm(@)r1=+|aH6PD99vHA)hk)Ed*{c^3&mF`XEYq*;dc%u%b98bXX}oxr?i2k07G-bp`G0kkbh)JE+9F2>UJ#0-o`nRY%FyqetjQ0b8^@(I>inh2j*k6T~7;)nf!6ypHaZ2f4<i1m;a<uD0H?DXEGQSQ38EADR3m1_)TpwWRWNWO=+G)OMzE@BEg8YiR-<C54BB?7X<O@eZ970N~rVi=yfIUP|uVy2_u>GEX;Iz>}Q98uNvjhDM{GqWVD2Uh2(h?q8kJKaYLJj5_p(aGSYNvOS7gMXIWx*7kf>djAXL-TqdL=1-gYOK#0VN+`R&OLH&q>;8A3rzfc!a=D$2PWKL+%En7>Qq%trTuRE#>{z=ZzJ|X3K%Bo3jyhQqQZ29eeZ|52ZK|4z)LX3Mu(eQo}@B@tpf=9+7qHy1)nGrTUx3OF(J)oXH=1`8Aa2{Z1E-=R&QO_jeBUu%);Z%-#2Qz$3LL9D`Q^OMItMis@BS(1{BdQzN1S~p~HqJYCJx1rKUm01%bRMev(KTgKj$9`^N^@OqQAjE>l(!wy$UR+xx}b<aCp^SA;o}d|y%G2{-ubH`ix=gEED3LOmIwXmr=r?}x-PiC86CfrCo;5E6xr90Js1u|S~+&^u@ZZ?%W$;IYw`>B63kAn-C8LPhe<r~fEu1Ot@@o<?A5ly&^DYMDjgKvDKh46y9eu3#$}6V5v5*fUSHpjKkRP;hI-k(d;Srl}JcDYI*P=a8WiuQ8-Ixu&_d#dgR9CP8{9k?HY!c}k--b=0uEgAm{-P6$wB+AfVC6Z~XBxDZUS+AA#FJ?kgohQ6*gZi=-ZWQu$M4qtX6fJQ;YN|}zT*Jdc+i0P@2jg*hule-Si?{6NQ%M8LpqmW%7vL%w(AWA%tOMG|f$G?33v3^yL-%(D;vG7X^)x8dUkqW9LPT;PR9O~i#<#8ELRq-Af9{RpGL^@RWz02Rv{TE=|?9~q47di};v@hSgN1$)LLZRQruK-T0Fa+T_aQ&+=cgn<GJl3kvY1_(6O0*l)3qV9!CkcgfQKSP(RGjAO*fz(!p+<9Grs}^~<nca7=B-Uo%P|`%m2zDWod7@pB&?GNkWOG(*)ma|BDflF$zhP$Fzt(ZytIYNzGcs&Y7cb~<3oF{NOTRbj|GYr+jQPqkk}DS7;EYhe7ebf&^#+C5Ci@TZ1{vbXdG=Js)3mBfcMf6q>;;9Ma;bbR&GK~t=Bl|yrhZ+h$X~>(c9@TAavD_5jTc$Zk2kOkvI~hQjC>mw6n+)G2^Nzf_DQRR1<wgD>>0`Ug*fa=*-4(l-YP?i+#9xP6PZxyOW%wA;cvZvXz&#4j)5N@;>w*-=z%=hnNcaW@(1hYozatF$@>WEpnkc^+4hkjr2YU4>U^O1>bZm&ZQao_%3joj!^m&PBkAoRwY+fCzXM>y3_^ePLpA&+(pHOY;_}C{BRkrxHNA))_QQoD^?b2z;TMsJ<oTf1lj0~X(z?T`ZrldLbyWYcqZ22z=d#ng+*Q#W?$&QFRriq#Dy}T-{sYKZy7P=CH!=kAOv{QDk{sWLcXo-qkq~pRhh*H;`i(p%Tm#|AfzBn1)RTh0HOsu`|JeQmWDmr(xBp)&P0E9;BzA?Nn7U8FRTD&VmRB}pkFYpBHnkdLa7eZjnao2EKwGdOb~4lLQZamH=1<QFMxJ2<esXXU7bgrr=o=BwY_zxpfpv!wkUI8_abZ_P`9sT_<JnUcW-Y@M`H$ye<}qhJdK9m1MyG)EZq`>=#Kppp}nNfE0AU=VmC>gvFilIaY-4}0*@4|do|d21}P&60^V4dUGc}}VK3wDpaWM(Ly!ROLf5<J;qV>fx%|^?iJt=jnD>WPDQ7svF_o1$>X$zkt~xp%d&q{%6uSXq^di{Bq*;~LQd|L8{jRKbR6;sFw-ORk5_B8#Um!ECEo8uA-l{WI-7tigYmsN8B{@;ynD9oqK<XSISs!soKDCn-EzeiZjXpanEAIf}D<?9AG?sy0i|=6`_W|_HG(k}qEdXz;%!_bNpYlvmhP;XG_dPJpoEDPUT~3bBV6GT2SMfGm1_d*~uyJaZfZxV|mx+N#tmtWM47Wlv7j}5|jI<~vKq+}o2@jUQDGZXJt6a<1dcU>9-?-Z>z7?GS`g+dE8p#vED8$aQa1O&J5uDT=(HCR`Gp56j|11fKNkfRrQKc!1y0QOL10->1%s?c_5qE{KY5`=2H}B;ns-_3xV|_|XIu*ADr3=%L>>tdf6UWh<>>a9RjSf<*G8J4Seu@)Q8dd*_fGt?%oi)~W>=v33^ItomRi~Cy;Ip`?WVjE#WY`ngaXXhcm#t0B;fkK=lCx!0sdN=qG7wf>vZk8L^gY1%F`l&{|5(8u<DV=p!0X&%E)~h;HM0`9581pAD?*JD!WLAMU#EPLgSFKm!g#3+g$8%j?3icN34%5o<~>x)$Ss|jPmu&)ya{K$8&KKh!=E%~Q1O_vnG?o_Q@`w9G{a?wdzw$%RhOag@7M-7Ta-)J>?t3D=~nOd2~pA(1|t{4&kEh`p?H&z&FXjT&`b<o$gfXPMw5o7)I0l`jh?ndzn^6&__$C0<qy$D%t$-@EDXU%EY{5jHxYB$lp=C7hspc95D*J95_mphRiYEfTBD7b7y1yja_%&sm>b3c4GRxL_LHQ8zgtu+)h-qXx(L?JK^R1rH4Qms3QKr%9KO+AZ;@&3Qa#o75w{PM&@U2eO`utfS@D^*nzin3W|NUC7^9blyxt#;a9<mpLa7N4$n2N<613J;oDCiuF-9+;n)ln2=t6ctRC;R{QSzvxP=IT&DvVs4qbAMjXrq#DrIsy-T6{btt*`8aH<3+Mm;GYPpy&&$Y*6N)l2m?$B72&U09~$k9JOp`B__`g$iz8q5rn$E&D6Xjh*XR<Vh!S!QDJ&GOV$viDu3`%4^*9#;f9rEMHlyM<{3UdH+U(;`yHHphRh_UvWWjmhvxy+hSW#Zz^C|8c`71}s023cl%hD?JVim8+cMC8?Bpo&Zy2|+6o8TYn80{gA|S~yvOpz@s0C1H;u&a+l$yHB_aR^gYKn9Q7$&dcZMH?{#8_Y6y;a-FLwZ{r6z}l@^;@DsVv3)EvC0m0Aw{MQOv;hn3%V``aY^<agGtDiEruZ@nurGB1y$%<*~F6YP3_4PT|q(2_DoqOys2VlX0b<MP@ezZ$l(~_3bK!ZiJttFnjxNoF4!Y6eMb<$RA-b1J}idnum(ESs(oUJI9g|VaTsQ~IR&f8>+Xu5IG9k=@|jKvZ#`rcizktSd-uDgQ1wM=1nC34as~1%)Ly5E$dr4ATF@ZYmkIE2`YHOXdm^RJwfZ^YM$0-PK1@|{++MXO^ISBPefzsotP%Sg6KF2L5;~YTPh!_p9JG^$``t1MDWQz}zPfZ;t&A3af^HzaG42~#7yEFT{ZL04*RlTH$6Zq|HT%VlXipgw!Q>M;KH^qMmv5F5PR+ItqDo2~j8-UJbfJ6nO(dMQjsXRg)uNHX=M3#6dpb-Zt=|5w5^87Ag{#GR8>c5FM|}+C-8oh?A<N_|&YR<58xf6o$#Bvz)74&id)IaLQx-f>kHO4bd{n8~M305?(^H=Xnu-lMs||7Ch+{96K;FTmH3~XQEi&Ywbvmv$WMV&tWxGjDRKMq&j8J*BWW4G|!m8kxmb(;9-_wZcE0j=lgFTYePNnMFe*doMj4nDapaZgxu9&l7$4wd2kj{8S&MseSN<!>@%_M;ob}KP@@N8}G+wy6d1r^)aWbpggxN$^>J5IpwFII=PF69VU1iRGAxM|;(WZ8QO8-tAkhGKK0?x&#DsRa7aNw1}oi$ya;dD$K&kzws*iXs2<I^&=I<6u&#??H+ZdwnwF?8ns!!aS*0X_3d6Lb|(KgXCOf{8Wa>!$O~O-`e0NfMW(4V9Y)qokC&G?&e8?QB5!X+6Se~pan(5Bd;d6$ACJlJ9zzuNP?bCtVndyI^(;WaT#dS1I7g^Jr-!FMSb9f%~M#SjfrC3kxu0Zo8(q)(rf!01Y3F@+wLTKbNi(|gsDR1*^N~8B+fnTj4bn+W~rD<-FAZ}1ItgXQ0Ios&)AYh-+vGX4~ZUvD@G5%6}<TP+(1mCuI`gjopKB2JDt29V5inckwHd$(5^Z(Z$l5UW>KzkQCr@Sj}4|kP+8S56*>~2QH8oA){Hs7wCY5~_KSCq?1`$PVEUp3F$pz#C$LOw9b0r5ZrWkod~$buUZU|>fSNc%JqN=3<RcDWBP!wgsgM6Sf{)8w1aU%piSdDyjZa>Vl-0->+x`4NhEH{*=95^sb<wY$^s)G|npR1N=sG9SE_!`$*DlwxeMfj)1o2Qe*ur5q09AykqIj@Fh+z`V`NW%VYge*)v|nW=^aGH2R<gIcaRy!YsKbetKgt>0f;3doFZ6X<m^Y_jj_?^2E3_0U4}2^kCQSb50|)lv5w%qK2q0q++pMI9mGOwnCBfF0ZD;FAnYd#qGx)w?>pT$!0<w6rSZjS58gF2Cd>jVk2Wfluw}W8vYpY3t6YD8LrPs93IPK!2F?G301VXr;VrpueMmMg549ktRN(WTud-eYw1MA38^`nIgF4qCFFjQI}+bSV#KQL!FHNn-@k=VIW0ung+qG*Oa){oXGr@bLNae7Du#Th(w{;#Wq!=0%2XUT~YP4$N=$7H-6GChhBzeP!UNZVG7FEf3^yN^C_L-hXK9US1sxh$(@DpQ3mxI^I2CfBL(2t}IW;s?!s;p7j7W!v(?M^*ARKZlcJkqcWe9kkf|PFV1OL|3y(*ML^!4gI?zNtla5tSS+y7Jg}0Lg3Ea)}!7{A_NwA3YhRcT2xh<z<w>OXJDw&Inf#r;E6(_q)?o=Rss8@zXz`APi7lKdAdL?T56YNt}T3~Ow6P8lm~XrK1FQ?+(Ocm?DR#zV+TuFT+CQ422?EOkyEs)dU*%NiQnYBf!w&*zL~8Ev$_#0t_}2{=1NM8Sdvste{<IMd$Kcv!ySr-Vam7`U0!c{cMGj+Z^Ys>k+%B!s{nAJ%}Cj{dA?P%Qe?FkO)q6>!iag;+)R65h$?%uT^BP^j^;Kb$4Lo{rXuIL$b2i|;wj#Y2uI4^&o>h|RyIIwDR&s&UuFWnF{Ark@E{jkTqQ3IJ(MJ4BIn{Ni}A4ZDhT!`Vn{$|v`{6}Mg(d(0T~12X`JL)8q^jigVd<jj>LAFZe7t0^@mvwWXq~N&R-|zr!VTxc)I{zKTu^pssPXh6SXvb;BJVaPmF0jn!HYV2npkh*eH6mM8#9$rfN^;ZRs6H?Ic6`YXg~y8oa$e>sq`$q;JQ#Bupyv<QEvlWMo<2B9Ka7q=YOm4@{o9xEOPd+3$~A5OT!_xA%tHvJJrUzN^4M1-U^)qf(dKdXJ?znVCEURZ&A1ZD40=3H50z5EosZtEc+gcg8q*gj!!l$}Joq91338v4&<8q)RH5GJYB1w&FOivP0Wc^vUa>6<HK{j%+g5h8)T_)%|2S2ZW$2CtU`29h#E7Yw|-WiGC{e)ONo3TZB>EnRI!5HarIZ7(W_sme(%IU5jo2#ulq*`-rYXNewfPIBn63R+bwveKc?rZ~2ICZcd5n^G295xMt7I%aPci{dm|Xb3~1&UO7B&u$(jHFcfx2pc)h|g_B6i?S8jr!?pIQ!Em%CS-M4;QY9mLtfzbE4KS0K$#Pn7P%SHLnEW9&_?<8V{rep3w5KXmnrg|TnnwHmTnq7H;^rZyATd58*x$vxiHU_OTlm&pvVI8AT>^ZDoI|MIHvyN?#7~>}fm{LSSWhEYmV<W5YA0kwBk5U;7zj+-R--ySttWG$*>KECK+gh|9-$S6%TK%tt!613AmowM4$f$sWRzmUliS^wCk?3^q)|Op+e-Mun;Y*UY4TFyHQeNq`*3*i(>{-W3att?%}ogWe5sYn3z_#U?Q=4F##t37^`7UB!i7Uor3IrrGi4`v0n~<RoQcF9f{BgTuT&&Qwuijalk?ESjO^PrlLhlKbF_`P?<@So_75J@Ujp`m@}_Av=gv`j>1x=NiYcu=nMSk0^*wN3wL+Fc1O<Tr=@h`-a{ug8p~Omb%(WNQNip6*weC=*8V_ATn8M#LD^11U=f3eCl}Q{%tma&%S?|l7N}+#Yw!z)cJs6d1gw!PIvK5QemuxCTk9?}qZ1=ly&^}BPaf7!uK?Z-mu)UYF|ADFVFFxdKe%cVU_5mp!IRDGtyo~tp%$<TJVfab?_LT%&MSgW{_T`T)XF1;`1feLseP=t9_Rd(g=tN~s)O4jZ(WuX#bK}x&D4G-VHq4z+6C&XgIIv{O#SHIv04gDVGen~{c%{nptEsQZlhb!VB=E^9U{_HmC!i-fVR+WD)|}G`JU$2FtxlkBY}^2oUDi1+C{$bI<K@pSJ{n*Eq?#<oX={oBm?Cm%;qgzGd(g5a;990Av}o>`nj5u>svbK4j>GK*TSx$>A;0q25V@ti#*3r$5D**p7r!|>u~FvtkYzva)~4cZ=jA)l?0(E)9FJ{4lhd~&bh6)7t0Lw5R-C<Ay@I}3nUwz1FW>+0-QU0c^5w@;fVTmT=+0G>RIHawZ`P8rCg{O~V)J{UL@|^I_I+VtgTyup$8C}xd^saNHWbtlM_QH$bL14n;vb(oSAMaB-1rVV0GhTL$6MdFY0_6Go=l)aBYDA#kC@KODC&1JJ0oOepeWZqMb&!b&rNA%peB$1)m(mp4(Y|`vKz+#4L~8Ar3ko$YC(d4i5Fx;gTQp4i(IEE{}`{=Jv`_W*5muUf?jYLEBCDxSIF^r0V%Kv^!JxQQL);TxuVv4S!zwQeN)V(US}kbq`{2AbI}$HO+2xf;y_2u>^h@SG*;tbLM3)FEWSt@><<z^b5XE17x(&4llK5`=PbzC;WOQXER?|ti>OY%-5+lrs1xg=Bbd6PS|Zp{j}OSe`3JvC!5`G=GsAou6FsT}sxd6AU0^Pbyza{LD2G+FBo{Xfp38;fHd)A;6C0~fjLTl`>qW`eN?jz5hi;cC14^~Bghru(&A3fEWasWEuS#h@UFD+i&~N&s1nb8rWoZ^Yzmz?js;DL7yurY#stloLl3^Gz^UIR=R=V(7`F<euK;lzVIqDXfP^L64fbTG&$fHh@4AjoI*|YLJ-aq4P@XILI>l^L73YUcuvJ4?^(=uMCK@RYJip*TD+2{x%!+S;E2pVv7<~ZNKV?u$&Z*ZvJpsF{BH#|$PCUz|Ocq*G1&3~17j6;P$4Nq}nx{t<qi&DO?iD|^7XjuIdaVD-|jXwbVE!|Ij{QYM0zy24E-02563N-sMrAmmDlfk1X7%Q`HerN~mzkSW;zkdIh&%fK|m(y!)`s&v||M}_ZN00sNy)yjUSJjo;t4~wz=<S0qL&@OJ^sJYH?XMsC+b>1#F?0}IJZ$qV<qN)*UyAqB96jehO)~m^+8nYL^u^nGPl0KFdHUhYUxkTm=Zi=1hEIF>w&XXP)v1Pbm$C{)QxZ=@=9H&CVT4H8N6!On)p|uy?@DFG&+i&_6Nif~^ogB`jUOtg0$_!&zQ~+^E{M;#=T(k9a$B1)@)hBG;(RY2`#R0X#x&D<=dIGOpWc`A-<tO!WxptC++gAjzZ~Yf-e|iqcB72$ZW9U%YKlfQCiMK>&V-69X=y@lE@oH5lu}>F>u_!06p^>FzF}h9r})+2#!hA2TX>VKKW(LntB4MLhgbOVIWNlZo`D8O7*S#txEwoas9IYqhFqB!2y83xrX1pL159_L#^9pSlHPbuhdJE(n%fLB@8q71x0FX(8tt~3Wj4k}`fho|M0_x~U6$5n=bNr9xBjObO82(EVlD6v_bxOf-nW=fnefa|ppE?;iL+Spbiwl`rA7R{(k@_vPXhr}n%+@cpgo(D3bJq$*G6lZ>uG^eU@hNdPi79T>A8u7JGBMG?iz=J008*Gmo?pcNcq|8KvHaz=7B}?7EbSmxh8X_O0})cSE|CpomMW*`x0ML<0gTXZzgyKr;zL67v^POW1V0EGW_mdDTJG3BpR;CaR;)kMv=t&X+|C07o{rtb|L%UeO8wUZ>Q%Vz^d%=9Wr>=aHe60(aF*H+Wn4U7-TB2NtSkeUhdM^Ltm6g`aw4|6&oKG@EC$<c)qzeVm4dd&M%QoB96&4Tt+s~`V#cM8yfkVj?mG66dfGWBRXat(Yj-qqt<)xU-;vx=h24_!N!P>^F0Xi!lFcIfL)Z|Z?BE$Qc8+ki`TyJ+KdNH+_(&@(st_}=5Af1lCxK8$x+7`*#C-`HFB;<y!KQoC?7g}>-(fhNbi0*OJbmwhfu4O0I%hOAQ9I*>tfd%S#zO+Wv%<OUBUI955fH;DZ-$x#6awkt7YsFjEP(TSc!O%5Bu8B)k>-&E1HsXg2p{qvY}97W4^*F(bq`xIJH;$K6l{#Bz)s7AWNBgkCT^x=VW;PW(4ps&t`ERbgfK2ef-_??#|diUQYQJ?V2Hz+|TlAh5!}PQSO*mtNpVfYRaY!Ydpnc2lAAYCM$3Ymyi}<(*V~x30?K=W@?F8rCj2x)PcKVdF;Zf0>}2nx52MHjZ!?^DC}VZ&^^hdnOAB858yOfC+S11v&0*a+&GEJ7+0I%1y1auQ><+cLb$8ta0bbgk+{*|IW9}X;H!z~s4-@x_@nF5(s6vMiEgjI#`mzI`?$0ey8yE-j-OXg=9{$lduRGxNA0*;s}-@M^X-yBzdvAB)K5t%$aF3{>^yQvWtyBH!Y|rq5F*ObLA-F8U<5m)O(W5t^nYqCA7_+?V#a$P?XP#mcVF2}wQ+*q*ODYAFez9=KcK%haEaE+9NTZpd3F4j0qYir&fTi{-{85f>dBYhz?5B+Nnc}!z)WBO+HwnRGSL9N>8Bm3;#O@MWS2B4k*v9gAoOi7hP^eDXys1|AJp%$!_iWQu<dF)1myl1gd93>;Kk*SbRvzA)=hVlo=Ibgv4Fl<Qh{9_WOmLcoL*>)_+XNmC=EwEhbFCnQ(Z3g(FL5UrIQ7@w9DR0bCf-<>r8lv5Z(#qslhWC?*OoaXqF|0W?@qggSGuvb2gC0l{9;O*CWZ5!h!3jnURJ0c(1(}!_Mh9low|cTdaPHa&hHTtz3Nk-q;Aexvlre(!)clu4xPt;;mBP_3Vnva9F)I?ZxhGhf1>Y2az=`N8yba0rcCJ=z~CmlSPb{+V%Af)uBl?FjGom6{gG&4=_ZnTjPP&IXIqK(9GF@V&CETG2}-!?@6c6#hsj3by>QxE`^;Iw-7Nbg2XeiX;k-(?pMkvB+@r(G(iehrD@JTh1%oDsSd}(+iJQRpEcHHR<IHxE0i6qoYry121-vDe5f(*;W&%0<0`D>J1?!2K@wG_2{zg3-8hGC7#EJhznzilPN;OFN6zYg2}11Sj6(F<pIZshWHm~3Y4%d=ziF>b%7G;5D6tDEtyAgPdHhA!`hJg9pcFnXb^f|-2Cot*hjiMih$<B|t9&Nn5<O2@9!_P|F+d-nQguxKr;^Sy?1Q?;0=@O7F!r(obD6Z(ND86%lPkYBAZXtOW|Lfe7**hZsxV~_9_tQfFNlT5Vwo*$YQpnz{-Jdi8Tv!^Bw4MkF6NMBIg89GA}M7hQ<=;?<Q~#sQQLz^gG|M~P$k8c526~b9T7Ckqkc>x)K*ysuHX&Efu5cWHG9<>qyR5PjFs^W*Zlw_$aDf7s>b0pHAvdn3~UDRB@r_9(bg)rR+P1QVrDeao_I1b&}IcT(hnWUI<%yJvD`Q@yh(?Y8NSBL&MG{XkEieR=OXX0-Ykw?6Ey-Bm`VuGGc}H0GkZSHPtRi_AOV8iOXgC=DtGNF;s(o{MoJHD+M6ogZ-HqEO$At25#tL%ff^t3IR|w)klUzZW_10%KsfJvaIO*yl@HP?CA|%5TKVE~2OWt;|Fh#VTmGL&%5Z{qyIh5K1y3YYv{MP|3XE$jwAi(6HCqj&VcNj9OM4Tpsae|c$K`bz#zPA~MSXCic0|i!hKwYAqq&Gz^b%q|Vi%EzK^v;@L~{37w2#eMF)+{)v#NU6pxm**L?&_w!q%{_VTr9wys3`{hB?{O>?vMn3HPGobQI=QW-hKjM~6hb(jGDCQ<*sX;8qeF<=c{YjpVp(fyb06wjU8U@UJd+AX=kKD7VBVlCWQRQ|SVB9~xsc?QH3YD=Mga#g2PXW>`E8KBw1$UXL}5S#&$ejS^_59RtM@&PcF`<*b`L!@4+ZxYwKN`Y11HL&d6`GgaezowupLw-{C}&yLmXGL9pE(at(c?R5-Bn<@G?w84wO++#Id9+>!CM4*Wo){uqwA-Rc5Du9Wh#UE5btN>PDj&id={8o*zt7oa9Qaw+OQ-XB1bu4;~yC@O-FJHd={3P%i8YLt~cXG;;dMe<E<^}cMF<4;w_IDkD<d?sZhz0$c;xE-7h@0VkUc5YBJp*?WFj$Tx4(~vXG3U20{eICtJJ_QHEqm#T{PxRM&|c7z&}59xoqC@>TFZovkipbYuuZhUL#aUL6+ABGc1T53s@h*<6b*X^bTqbjyLq?a)}EYd@aAtC9$2j14G?f|OQZHBr0mZh-;6)r&)J^H%kUG1DPbuAwRIjeRKmu%i5we8q+8Nhqa!AQ{Gx}%w_4grGRqc$Wz}NGZCGG@{4zH+k1z-$J!@i?ByP2V)nXU7_*H(I6i9^T;T`>hub(G$RacIODk>gFh59hO2it***_hOeesF8~dt{XYt&oFkvk?0a#BC{G?0hI<$6}~?<c)uGG;7w!oRnyaZnh?I`^vy0!nQ;aQkA1eQ`*39LsvtuMY-Xoa7(PqwE_;?V`mqMaDWG+{mqR(;qspDW`g21;^rxBP{^87ZF|Jh;tV}*AFNt2W^qFCwKn?c&MC0(<?><6%--gO_K?{>c6t!PzGYxN8X$pdhI^-w38RWh<2<v`?XfmOduMQIwpobx#f(%nb_n&kJgaudOur87s3=cWHzl%b)F7JvszhswI{}p&A<}9%4m(=a=afS(j!>Xr2_b=u;;WX^+zuY5!yv=hi$0OKWQsPXTHB>+D{={5M<yi;8hI80TTc-4Rgka`t~GJ|i!_7srhFt=Oc3p6K+!vmXfvN{o?FhQlb<L3s@x3ZraVwlpLF11+#PG7b{d0S8?~)-qmodMe*gwZ;}Zzy!O5F7>FR6P{bSe@o539H27C$R00{r1p@FGp<~ogWY(N+CGBxBEj$PV?=vbVOvI62LrdPb}b_H>cKUA-S(kda<FYWhgJja0)<?A0#NtsJ;f`o?l(X_;_1WaArM02WdgJxtt6*_P%N;`=9w<f{WVcxz_g=>KFroaeaVb-r3rW9}ImP)15H_%9AWoY9iMfrhrrG+A((XPhcejc&grb4#2q*sewblA9wy6~Plsbh!bE$}<7p<4x>hL96$l=L^LHKxb&F5-b=Ix!$gvkdK-qb4aegc#L2fqBgf&^5NahkmC2XIqe{j@kiSjHT;|85of=?R+eFHM#MjQX*Sq60EZ{5k#>bx4wAA5BtF>#sRF^^wAa&>!B;kVG@Ga>AFdy+;wkP+})ll*BHt`odfxgd=GDFkX+7PL=|+@O-K{QrLQA01muUC1m)r?lr0{_Ej)E|I&yZzNk_rc<;x5dil&Y@LaOT<FL&W)W=U8Ntj<vpF>U{L`i>NQh{3L+hrvseP-Cx#|139jGYVGKo1ffP=Jh~`xC{H$Sf4GzCe!wvdt}>4BW*htnE3gGgHn4AOt`_dUHbdgsjAvZ`+fF}ne)WnM!ba-Fig@H0@CwDh3N?X-Vb{Z2B-Fbmtc(T4mY<vNn!+B2XOSYCqxYkK1C*WwNx8oLYL3ZsG?ajil&p<;!QTJ-nx7n_t1u!g~yw}Z`5{=e?V<l#=NSRL{>6Yt(8L!D570_N0*#JhYe5Ea(v=SO@oLF0(nvVBzZCh-E>&@j}5SyEHw*UrmP}tU(fEe_lvp7=_YNj2y-U+zM{kvZt&M{uFw1iSqkNZdICbx=&q~Z4~b<GrAo8{2bJ(4Bnlfj1gOVifkIKAchCslY7f!DW1}t8g*_WV;AJ#~ir$@1|54Bg1}Y6ajlk3>>-b^SGK;{0qU@U(VA-l&!B#R3oORH#XP#<7t;B+%-PVdDF)0vDQztM|PS^I%AwwlbV@PjuO>=LH?eGaqg7i)z(_{AXG)8OEs9}2tA;3|V5TMAkT^d0q_{oBHA(&#dS6H%p)=$C>eO*=D6l*`o6!`!gzU)K*jZ%n}CLL9;%}~A((^DZE$sV^ScO9JH-#j>%8H9&MA-h0iOC+&Dk$51N`0mn=fBF1l{i+_bqnwaq;g=SAdmZ>96;w%<z+ELd)WreH<1(JA;yp4v^nG!NbV%-dm%pF;FTl9js~x&8bQo%AU%q#bI^TMQLb;7!0i0N22*PvV`d4A@l!?7~tW}}Yww0HZXg8=AfQYhA5(?*{NC%XtIL+3vZH{?Ejpn{g)qk<b;C+tFTbrO3Vm4AL<+>m`0e}F=Rwof4oxrlPWg<OAa5dhN!yvO^+86V9X$zHo%brKo9_k>*hxT02=Ne!i3luH3>AbZdu_Kr;R?{W;bd&p_c~(*&2K*P;@CkR&INCx~1M%Sj>7^k>BbT{~n0o=N+=QB7uW{0ONfiqaONa-fx6@%j=;|ILZVcnxD)lm>awJHl7%R<aXOSl|##K=S?*=@mCd!Ida-!e7&=GvmnT_Kpv++t5`*8D|2Ka?`Cpkw$h)Xa8D=%psK8B*?eds^FOB)&vF%|O7(hRBBNZ%P_7%rAu<U)1ofn+Nh>3xtKXq3JSvgufyOEdEEUEnkwq4X!5YCd$VO0KL<Dg$qIsSD7ZCc{#>i;4@`>PEQu;WAutY2JE#_27zEtSr=k;}o5Hp6^Hlve6sUPKu3{Z?cSpaD~Y6OsvC!3*qz%i@Yq%z9@}eTwnKz3uQpR%d7F;GGfY0_~|Y|2=Ju!Q<n9Fd|TT``Lt`QGK&xN@7XPurJ`>^NI{qiIDhE?L<@HI*$J*K4STdjLB%nh$^GoW=SEbLw!oubSOLt$aJIQYzhGKLyzg9pQXQrnnGZEsqAVtXAle{=oZJj=H0h>a0PSMPJykoqI*&R}MG3WQd+Sa?X{vl}QRcwzMc6!`ZePpr_gJLw-rksw#tat!RLV|xN)5jU;-CImx+MtF9s4Ijdr6;HAk9$3Zjv}-*9nT_k|wAH9w}J&YOwJPQbr;Kys<F5;*ZV4UdG!&2d<EYAnDtMu6NJF;XB52`KQ?uKL-LZ?+>j~&TxujDl2o;FMlpvb#y%T5Db?ob_2%fMX-xWvns8nxB{^HU0Lm@gmipvB_yO6=r-iPKxSN9$biMXRcETYVF)kRBF{!ka-za9;f->E)Hy)HKH`vkY9}jNp0Au6eRfn<-T}l{PGkycECan3-@`oa1L&J+f}${50Nz%a7vY>f<(Z-kc@x|3dtjP5EhMqKoE*8qTrps--)*)G3TA*|<J2qxzl{Me69bP}(bL!%ZiQwp?C|UvX;DgmQu3Y>9xQ=V7$iYgxt6c>ert!nakp7~D>?!6^_-J6k|%;uh@EHQ9EMFIIH^0LFUSUFOot!;SrQVHh7gsbN>dhfWB;cHNaE0#fk==e?h0Ym0>}<;-pff;O%KG!`jnP*DsBx*7p5WEKbT7=j-xr*J5<dY9i&)gD!4}c6ep%Ms{R!LTd>MIYpm_qEi@tKzji{aPA#XvXK_=>a36ZfuqU$Pb}nx&TcMi66+P1>XUnKk=_;&bAgsD%O*NP4dw}s{JZnS#v4TCuKUrLW*SW=9Dw4}<W+iYRvUwj?gc>D;EvP2HPWd7SYpX+q@lqKI4eqGfG0&(I1Z_6Vd#IL?TRJnJA_=~D6V7@!pt8${KWWaO;xT74CyWiJe%ZZfhRY83G@rJsE<@qpu?=vxD3`9;Q$7UKt={buqNFVhMlOb*6}sC)@g^Ue)$iD$nHao~U!S6kCJjxgclI+IJ#C48Kg&??ai9FlAEJ$zk#_i57=n*jteX#RBIdFwMdW4<llONaAQomM@O;FoL?@87MjJCP^dV~H+-X2DH;e-s79NJ|CrJl?x2RaET`UfC5v-kqFo-T|8gj}Mmhk2{e51SGBGcNXdaCUsZXYJ0UnJI=K(iRL;xlVCYu(+<CL>ocMlTI{y+0b^zBW3AQWGAK*)R7cXsxR_8$32*j9x-D@3$w>h3tT+^wut-<WWbV0M}qu7`Zk_O`6rwMkU=!En5(^_;^TKU)c$7BAco%`^A<)(HB<Ppv*xfsr(8>_B0^@x?Jx#YT3?8Or9T*iF4W_2z7g#sd+~bsTga-8pJK5!t`*KtRYBM{@|k?s5&RZ4J*rvF7DaPGkkn*@KT8PJ2?9cnMq7#5&xAA&jYFrsgJ6GPw}JjR74t432fRaMRB-!ih?w^WuX1o$x-CrFm7Wh03-J?f$^|JK$2l(fl3rn3!u=%Gtd|*HFcNoL%<Bw6zL2wOkTy?Y>Uo`vA(=}tG1Pg^tL!C-s1)8w?u`+6h8xFl^yCricA}rlq0(rbX^YOlI%MMlaMW23`0gV5e>o%s?fKxi6!Bi+LI}|f`XXsnX*iHQ^m~8VvoY0Jpa9s!!g1YWFG?)J^3j$Lp%jtut#G0jv#=k&L|ChSPa!+4Roqi`@|4&w9fS6FwAmu3RaQV-4#D^FrlX9Go2FNddMmkPa*~P?srR}>Wk6{(g%9w3glU+y-pF4DfbMuph2uJ6X4<WQ}kK)L`t7)^>f6HmUTpYn5yEqy=qV9xo9Z+_IIUNBlb5Y&|H8ebTDzA#IC70XeSN#yJZwoLK*jcb?LNP87=$--9UO{+&8i=_Te)7p^h@HWBt32yQW@h_KO?Qo-!zc$tQAr#I2Gp-z+7Znr$CMm6SRdtx&q?LigyKNH}dB0}3juMI(dH8QMwqbeKX~z5QJ!)Xty_SBvvDPESgX`WVW)bF64WmdRI~H^;*^A{z0M;iO@vtG)8}uIuclEO?+EgPFPbs8X|u9t-8Cr#=fb6&rF^8{)zd$6hLdyn{(=6m*taWXM75bX;%9#C{CRc9WW@e$O`<q4H?Sc-4)BRlzSUcPW~_rxDXvD52;EdnBoyO4YUf{$0@-U36YR2V@^zF=xY$n=+;$o$-jAUB1+mgxLL>NdhVCR$}zv+1lQ><<l|?Dz>r7;P<g{<A@G-oPgh7tPX8m$`P&zcBz$d)4naqviA};1{(zo#pXucPeH3w3G|_pUP~tzi)M)OvOP>9!`jIdL;mG;#y|bX!K6^%gA^t9`eer0kE;`ec~Y;^B9AeJba%G~$+^h*sSJ^ag+ArJwZTmQ#|$*Un0-7tg~FWO&65P9nqK;~4@#Lq3yO$GUQKR~0d-h+@cIpr1U;Krk?5p##&<X4GSH?6j0;qHEYMJk`oIgDr?5mD6UDqEoyrk5$*tO?*Y-CEw)8x<-AVN3_Dg#RQ-#X28>#F`oO{?AS>`j%QZbjh?FLN-mY-Uo&JCHLu_cSX{~!(?5<LW0j2?h1c=7SMftW;H-6x|u<rd6$I(a?7POXn3gN*o~U3F;Qh8|+gqFm*ow!9%98%%+qvZ`S!bR<Bd3Ux=U8FPMV)rpGj7w;a~6IDgQ^hFC|5^D5LV42oBw&*b2w8Oah<nH*qMB}jlHF1V|4uto~M;yLJRKoRBAOCR#AD6iZ;)M1R;{z!hpS&C?tC2Cb`}u(kpXx}>C$VtrqF+7fWASA*t&$GWbxxvP^!nbeU9M&Oj_|k$;-PM^g~M(Dst8j>@nDA#!z7yXi8tTYu4MCQzsgML2O#sTWN&rj47%=7hZ8M-lry*mX{e%K=<BpFZ%)A+;WH>!Xem@4_*g<rnEcTP4(!DvYN_xMK*k`pSxF5m;}Mrjf~_yx&eoGMamP|-@O{J9c_In~WbtIN*7`Cu-oWnoI1I=S()R3c2f^gmR+9oJ)>DK^uW6xi+Qmm>>T;C`gm68@)YLYOZd?Z$mK$r84yexe>i<0k){&v=M++BRt^;IYsI)$|RYKZ+V9s!Af~%_|v2&vYByjRY(F}X6AFWYNdqZ~O^pFUOGkECyUsnl-J5le?k`pDG>JL?p$#^?tdK4pmi<0z^wyhXnX8MMAAAR74=>54nIKYi_Sys(drV3kdhrpjru2bO=iZsQ=51ReL$sY{Mw&jJ7s^o2c4kyPV7q(zJXtDX7u;2lSu4a?20j<az`gcQ;Fc*bbRU%R?{L-$3z@53RN4=Xw2rTdvFyVW&sH!x9{aRMfz)+)eqBS7E6NN-cp*V4^0`^IN4_woq%r=Jdbb(s5)Go_hTlh?wm`Cd=5A2$KirNggg`_9h>5G8J4wkaGn6X+6s94M+r)X96@(zp>zsY$6xpA?5Gg}d6bt6_>8|XpJm6RB<B&nMI=B(}aWM>42I}{DWlyNP(yx#Wi7FyTdh{b6lZT0n60pLQLk+N;`e5+=q$Z9W|Udqyh5%aLQnfAaCRrYARE@q+}&231IlM)zBMb2}P`BuWkQ@j}wj+DKhZzgc8Y=GKQ?l8Q+%mjR6M)$kmK`yqqN?sUxC`rad&c#(0<6-Gl5bRIHkbur;p-QHW2-I={G6u-gILWg#s4Y$gsZp&RiS0Dqx}qEE53?M|mQ{J2zfR6iU(}uPb^*M8pvrty0iX*eYH9kw-4H{c7}I(*d7bhQ62=#?QS@kuil@X))t=7V(mRgYNrv>-1~L;hczb=;wRn3--;Qxfm{jJ;FEEP9$g;jgAeFvI30Ytsm^^cFG3FYx-ygRi<cbe&?+vwO8-V3~SAl^Fa)XFQr7pMi9!qgDGkFNAqJ}Qoz|PbX>eEypF1kEdPxZI&jB)Y^wZ4p$TR1>C6uhuw4b3P>msBcc{4&CA#c^I`hqkHclh;8jvMBN#*<`K_Ih1dz`^j<+2tij)x(x0*G$nc0<cCrc{Z#6y?R@dK2&1?&>GJw)cntnAel*@JuU(Y87To}hEmqI=5nYFp8fG4G+M*Y&EH`5MXy7K^@)6(MoD$XNjWA_!&7PZ=Be6mI@vu+kh#F75a(LWeIcLgYDC~|vH7HyPCy|uf{cg>MYwc5m;b=>;bc-^jN=EcpPxsIpU?wq><+R|ST2|OF`9o~*J7EU;_c_>UPgSTi)sjawjrRMw7UIRk%|lE<Vthuhzl(Vj6AM+g@U6RK{SctL1o#X&hfuw50xqM8pEmIWxdP6yo<^=L2kny8PRNKx(z6&b5SX;BMs<2xPv%6k;h2?xo&_pBLMsfHpLi8o%~Cc%$Rnv8oY6MPD8+;)x4SP-8d5h%qk5{gmGFl*H{M0k<fX)GxXC5=;qc<8eIET3S`})Vn-KW<QY)1gGVfX1=VbPbvno#NJ<lD53x}dg3r2Zn%1-hEs14IN6Nx<p6C1H#sYs4&4|%62=b?ug*|%#Z3+83!Xd7|gSNMtTA3UbN1ndRnP19`7oul;9)vzfQQ(Ap8jb?-Ed*Hrmg)D^#3IYMrDS*4>{@JHOiIwP>YcHykV!VTD-Jwb~9=d`sg}+}`nu@>Aed9eUlQ@i6&ACjo-j_L*LjS^SgS(%5Fe=vwsY%jhD;B9Q*;I%g`BbIZ?swy$eV8WV25)VG4E}s!doO4I15@W;e8}1Sv>|Bi15!G0{+GLX8S&wnI|WU`@RR!OD+#!Y{Oa25%O6|La=uFlLQ#7A&UPm4ow01uiOQU)=}Kv$QJ+8O#--a(G$-b5m^+~+M8YR<V9At=8Q$*zR6_h_h(>MjN|otXQ(uuMr|*DB;FDFruA)v(Ku>hS@T_C4Ij0kNd=A80oj~2#xB(`+taDsYsJ6(*%b#0(G{68zHCc?)))WIUMdZ@L<DV|~pk+(IwM<cH(cCjNH)<7CJ$3*bhuaIbkN{3Ye&w+ta!YxQ7f0zKAU5tVesgwWqs;Fi%YNLgO~u>J%XgsJ{g}fz9@~H>r*B8-WWTFcMauWBID4~t1%0zJDgCEkzW?F7zkmDX%a5f1Zv!0BovS9PSTC90tR-Vj(1QoX=J!I0Vki;p`@+HoiER{)+ax{saz=b?D5xQhv@8+k$SH`$KR$P^{9*^W@f~&mG;K4Ex4v!Dq_0jqnLvj|@`4v1F`buD)bD0?M##!QQLcT8s`bd9o6^caO&<TNx%>nj(u>b!H;n%qfI>D)5pW6Bf&>8*FUW=lf$2aOxlU95F<!5Gc+e-T$M<;!z2Gud?prIakmK<JQeYG4?=OL(VznuAMXmR;)S71drkG2;&PX6hgBgS8qAeDhcw#ZdfsUHlbw;CTtj5EHO6+1-e33NRA0&Y0qF`+<?)9H0?*ZP<S&*~CXSxSjD1#LiQJs9dKi)i0C)PzrFm*+>M6jbCACQ6b4}O<|Kd94ZhWRumdQ=BgV^~<bz+4=8-IeE24y$NME^Zh+mkY;jvXC_=Hddb)m%ZHAi;}OEx=0)k-7ZrGlxk%OjY0#Pahr6=&fQU7mC}B?%0=O!-}Flf){jxj(kyy@DSI|mQA@^ogMn358A8t_!!TmzmnHA5bm6t~{Xpn}#HXfm)GachOle#I-(f<LN1Y@YsGV=KXXSgmf5zG1mr<_QH`;j>E(;@M8A9BqWxP&<9N_yDnYmoE(Gfz1_lmp`G~npWalU`YgaV7-;84FoRc{b)c$QvG>{#;gR5mf1|0?qshYEojp5n%IAC2)ArF>r#(}+pYu=*$BOkBene*pMfx}W;^`_1Nm{Vy81(+_Yg3$ir2L_n-hZt&Z8eE#eAfBF2op?x{M7Mibq{qvuno_<t*LEbv>+c#B*`1OZdI0Fi)-@o={*x8Z!QjPs}<^J|dJgMc99Tc6!r<C1d3xE8}(+^+%3Rtq2|G#>v%@{uvtqS7J--|hMiuF5w6z}-aqw76CNH4q?ySgRyxE{o~9?Thz*0QO|U(N7lISj~d9PLqz_PA~jQKs;Hq4TyYXT0}fy!X$Y3{7l>iBoHjM=2t|{4UPl!KcJKFKNUV#~I!Hl{0LydG1<;Z~_fBdd;kHhzcip+@ITvn2Hk_izs}7u!txDxW%tFR`F{w?ytv3O@!iKoGdwZum_%`{z{+R?pBKtKkdp|?mf*NM6ET=83e7TA(zV&=aYHyn?x7x=5ttPsKKKbQwYxaBvMG`X|L~38RmDF53Ij->sU>DiU(9*8ThrC3>Cg%o?dD3Z6W@Dz=#E|<BpV8733{Gd>P*M<^iQ-bs*-M1o&BKbexf5U$Fv&u`Z0~KBEyGcSBlv9dB@lM%JepZ28H%6x7rDy7z=p1jMeKog#C%@^w3(>=_E`pJH(T+*7x&Yw(|Ga1$?L-*1Z~BAnO^hoPIjyv~3g8_b3SnOX>%J%1&nS)S))mlFqxak?qlc+2Ioh(D(^q@!5Qr(>F+4nX2_He9gTl!s?%v}qxJWj3EmKvoYp)MxoCCsd#SGKs@oDazJuRn^ufqKsZcPRDG8*SujdB3@ONUfX=9DqQ8=s4qncm)6){erzY55I7)AD4jfGNx}?JM?ei2k9J?n?EPV`$8jH$wdiZyFC|R;^V@M@tb3t$K3eWg;|8*wny%j3Yy-{w67O2hnE{6FW@@m7;>h?)Aqt_;A~C#N3PhlDpVPrhLa=F-qPOZOkJa)^!?N3mapRCKR-Ky#2a9e=r@-W`es$i#*mPQsB{x{sJXiWIN7HvH6U0#`AUB=f>zCf9vUQ*&M$i`|*rlU;oqcH*86prb0G9j*l;rCH8fc}`2cFjCd(9Hs6{ctNMhzG2VaWwkS)LD`n$tf%`*RDY$YM0|_S=lSDlINw2{3g?^lf}X+hcXewf49*bJ~Yis>o8H8K&Q`n`u_{Wc3UqW8&tHq65N3w`KC4t=%|Kp^nAp`X<W>CQF#O9=+{z1d`T73q`_voKp${>C^|?XT6k<u*+@jecxV7we}hU901?9F#qtNtf8Xm%0JB0N}PKv@!pqL<MH_)n(=zrv)E?T*!;W~I)C-%RLTVVI&@0;wL>9rrjz&mB>UW5OpXa0ys3xWdrsFSX?%5a!FKfflw0YDSkz((rkwgRe6^-=ZSYW4d4s@=ez61K*PgPh1Wq|SjiR4|(shuMEcx_uT8s6fQ?9Dh`)=XD>VEYJ!-t@AP7I@0Lxql?M73NR<A6$HL3ygRnJKZl#%qdcw+15|G>HX=N<HbRrXiM&nK%ay4fiYhosD<C5y1PVQc=;r%f;i?j#>hFi*=Xc*w-IxI=AlFEm^E%G5%A|H&^a=u`OeRU3_HunJ#;V=#vW%Rp4X$skS>LzMN@?@o#JquHPEJYK%NntOC-aCI`RjMsoq<bP~S)->)~`cd-HdU%q_#`RU?Q=kIP3fLJ_9@8+6)#tC^}hOD;=<!WOx%aPZdLiW=R9hp_zzFW<rk<Rxn9%~$#XjK!FT?@q2DWWUZbZKF+7iPn>E-J+tUaoaSkm+3^4X!?&G@Z-dn;ZkOXZKBv*Mp?a#xssPtm+=h8|^Q@dYAff<$*&77j}5sY0kqWKjzR<b&RyDQH(KAfd}%-Kc`&niHHL{P1%u3j)?zj3c4n>rJHvP#jjz~r2YnDrQ%ePoO40p-&&+6gBh)c;<$p@FMIZr(UO=zg`8<eZuRz3rMyJ89<pAWf}VSloEx?(U-`g?J%d}y6LbK*hR98o+xGaF?i#d97e})7tF(K&`1lHBS#ZYWt=aombKcMUsCSsA`1dFqoS%}g@C7+TQ&wP)=sJjhcocyd$y^mBo5`E?FtiGr0{oBIY9~H;vucve9D+!azgZaeaeNR_ul_rVu!t0Lr0^a%k{Fj|TY-`XYaIzxTBfJ6`!|>!QbtK=`l^aUr{qejLln4`n>@j#;apf4y>X@1!?tgBkvCJu8qj;kWLd+1oix-zC#}C93|ZxML!gJ`qMI}F4ePw1l-8hbWlET0TgTwBF|6xK;Viu?FvjM-&P{2ifXsG68R3!4j<^_xG1sj4_Mj?+_kKFR`5ri6D%N3$b3(HGMlIw@81gY8geDM~K3uQAl&_VohRz{OrN~1Yb*e21@tw_1ObjH-y*V>~igZ)A>@wqFJw7)S&|^{NeI}}UDVAymvAwV@@rd<-xYK4A1tROK7?HViS_~(4>raTx73D7qdzyOkyPBkI7fGY1LPu$4ii2pO694JMUppHrFDIqy%;<67-YAsIaL92A+6;GoAtQ7Zo@{s4Q>PZ^vvD{yG{U{hQlU02>)agkR^Lir^o063>$c|MzE7Z_R8>4D0&G-Gq+~k=Syq#IR(lplq%Bu_0%1~m!JQbXo~%3*PuMcuQd;y&;cgun#WtyGi#ioOgsLEc1^))OPe}?@7Q-PGz_9LiZ&%Yc&Yk@<(GBisf2?JyJ8jvv>Yz80b*(|cFMG>u^paVDX6u>4KYm>mo<4XLc%YDnJ3YG7-YZRAqFDco&pU@9F<c(>-HF0vQS}r<DzJ(z1%%1GO{<^dpZX9G3z&=5cP@Bz+Rcx1Il-7tQ!W97$~k_kiI0VB+6BO{D6-qM3=1)NQ|ph47~)rJy3UB9QDG0piPwPrj|8UwSmz?QSAmzFKF^0|p;Xj#(!E#i7#`&szcuPPoyU~~yR_>nj^OeVJydm}D83D}Q5em_%yE(>qMQYIq~X3xbB`Sy(%O9^^Bac1_|r(O*bFF+-sl{nwdz~BXIU=x!wDM^@FxZV9W;JHlE4o!0<7i}=V~$*gbTgKDlw`<(c^{&>EXFG!VpVRcgAb5)SEDATMy5TM(;^5JQ!0~T{Vf1cZq>_kyonecgxyY0XFt}|BfSwbni75!g_hDJ}knz-JfDi-w_dL`pNE33NE7NcY*ax`UqT#bkTFkIe&SPZ$s5q+96{?QDe?NOAIO{ubgvsK^03dzhR)p?YCowJ!^#MNQ;jV64zldB-f%~HDT7<BJuMoxcDgMSR-aGKCd_2J)g-B8O;3r%@SfK#%m$XFaJROE^8Owc;i&^c#|T{>DC_HB&^Cgi$SYB!><mR+bT(Ey!zdtlRQ5+7e|j(uP?Y5v1bK2gnUEJ*6cXJ04A+h=b5m`W{q^+C6(3ngz_wmG!Df}s`nuA$?~9z$^6$zoA^@t^1troeec8%a@%?b0tu|@=qh@9sDW~_SacnklD#5`PDv|vTa=6yf!Ry^#7=r_*wEGAP^03Q7Bm=}cM;IS9E5MYfdz0a(cC#p!ugFruULc7>^tUiidrCaLLe0#!h*D!(va7)(ZlSA+)#w<TXUPtUMx99t>A6C=J-62`gW2Ylp+y*qkWy%Ne)Jjrq?LCMtl|=rli1lr@Iou?;W1APdlf4*jILPBXCF^*Ba+FN7NRGZ#L(0A)!L4mh2>$J5u1kh+~*nX(0UNM92H#A}UJuE0?t{LID5{MI7C#gl&w+okwb9(RF?XbQe{Z&EHkX6H}jIvj-oI<fC7gO@<Erw^_ej()lndQd*)GqLwr;|2(ldY&5p_TV-|#?_e5`=`@QlqBND79;?^}DGSgrxm~g(BbvJ;u*$pDcS72T@S;4JNM}tHen-k)#1qXTB4Pv)8t68v>^{qY<QHK_HD35r@09OV9r37ZgeTPP&7y=W2N1Q!Tb&Qo(_+GJ##oh_B(~r>%x?l^cP+sslFLjrEA<BL>Ly{g)~w`%pn@8?5f3RB?a|bL0>Zxtp*WSQSF&W~tUglhrL69SY0x#&plI+cQ;dx+k!nwFmZ8PlN4k$VnIfaqzB0BQDouKPC-KwlD`_ls8zS@Z4}i#6L=X>++yFFLxII~S$6ir{S{JS6k3l`YKn6dhHTOYx2lYjkx4i8RILn3H?)OdJ`RyOu03GgR-XPRF^kGDFjvX8g{Ju2hXieL_b!c!XbOaGsY^woH1~fohL!mM(T&W7y<2PWcq*^?7u=rzCHsfy)G2o`i;`j_?7-wYG)W>b3v;A>wxEV*FzC@7+>IcMnL(k~sbkM}RXs^@=0hH~972T3n$G$IBg;ldzmOvjTBSEbyZKt`W9Xk2W>_K8tV9v9{NzZB{^+2pRu`o@Ab(JI>^`6*fB+5Go1Tn6hh$$$>(6H&e_&i{Fk0YgiiWnl+Mf=_A@T+|iyK2VX>yr96e{dkU*h^s4*So`v*+UD03GrZk7?@IC;>tzdk`#}<uiU9Pj*#}n^!kVOag{<Z9XJ<xx^}PR)x{FQm%Dhwet638YYsTb3Jx><KCclZ%QddeY@46<7OElIX>vo$Y8qLSsipass)v6cI#b=OBLD?0HtSB1+93o1FPtDXjf6!V#JXH~UbI>@OXZ;A7C)X!m5Q5!9DBprZZVZnp%a_7qy06erqmhnmE7Z@?PtguGZ*cRnKoxS=udr01F$m4F3VetsL9H64onN_Q0UT%<+t107&4tGbWD!eHW~&XU{lUT=@Zx$YKwDW5@+I}N#SVxVKRROyUr~9G=kr^Kr15#tg4TnZeD#94zJ8*r5NsqN<`4_#8yH0*TAvP%5X87j%@E3Hz2;bXpUa11QY;oaRg<<5#60<)cnPNhRPNq?i(3_R;WQ<c5JKLlJ>97IS>QtroDVNV?G4>YLYp9pPHVirbgaf)N~({NLGLeLyOI(j{9iTVMr|NVn8tYC)a4y|93{;OhYtm_-Tb(E;9tR^O2HVCEdjfMpGSE+bCiYJsCv51XkHdbeRb_O*pY?e+_eM5HgT1uHd-Z(eNrI0k12frKM(D9`Ui47znwwCK*<!kBgZ=XlWNBy_{~vFh@f-OeA*G%tpy++6#I9Y!}l@3I8fW_cWXwVho6a{r{`(T$bBPav=IcUPvS@QTt{%X4MnD;Y$Di8#7})OkN}o5~wRX#w&#+i}!)50uqVL!raZr!)7+<Fd>YgXd%NjYU4Si#}XdL?Q>Xc)soxRj&DRHNoX$7dc}vyK(xoI7kJ!#JG4a)xbLqH0Pwxh<4r|V-hQt-=dv0+sqZd7er#sU-*V;0`~hUucrvE$2>#H`2W3h?Go|VkG%$x}roiTYZFJ_#Ed;vO`j!&aCH*7h1Do8PO$43R>RTVY7n`+y{r9(a=-$v_Sp44Jw{bgYfh%sIn1SP407ktchQ}0^E3G2jYvQ;aM0xYakp23Glha#H=sr24Jq{+qTfixQ{p&|T4z2_>7%BnJj~mFV73fxK=Z$So`~Og-dJb>8U+gsN+!6@lm_|~;dv)iU=l-o%K`c+E&hYTCHLG8g0rq$!$?kxx$8Jxe10IgUvhV2xW^0m4o9EY2*(Fw=*O8gbkonaXk_-^607!d^!Qn>JR;ZGz@b;U+0?gqOncAhED6~f{B>@H5BAekCI-~T6S=K=Z%gk?N5f4#ZD<?wUtN&R*-WGpvvGDx5Hw&X`!xZfi-URDuuJ1MXL82aWCPq(QpnW?2cBtgJkyFab6j%if03`ty^5DMR)^0WP&LQYub^}cw8qZ4IP<r=R1j%VvG&sKW{fKBfyn*tA-uw0>=rXQ}TAeEE=Od?imuLCG`7@W(Ou>4nRncBJDWK^DQ<E&~g|T&lxEyOV;O2|l+Q^q0&_dym^;c7IH231n6Hg^*8faIe>(@rk;9Ng<MJ_bPfsOnMD!F!&RD9mb2RZmhZY^;|j%6^u<ueU`+bIVM@4<+G42U=Y5DtV!8x<IGB06BO1@nF+-=-(2eDbn56iv^{G$up9P0T&<3cDKnBCP^zzzD;CR!JtHlkE>oG>yzUvZd+`?ooYM7V)SCugPEtSr$#u!m36v7%MRbzHax#jTHbA^t|y^Ykq>t+s);T9<P~8z;IYcj|Sx@4M?{GirM7P&deGLf#T5D#h{n5vh$YC{NC<AQ9}QCY984Lj3YUv@J-7J$|h0$&!ZkD_diCUGTlt3O%^2f-v}WOIWX}JP~V$g@z^BN;<6M2C}czp<!gV~fx3je{1BY+D@9^~5Ykf6b|G)tS1-)VYxvCZs(~rk;zKA5tT(z$bX;fK3JcoFCQtTtk*?bgYV~BfLe)r$i#lMW^)|xWeB<=EZsqgth`e$4_-&&)^`HwmVz31VZYU-9VK5MUYc;u6W_5Jc>1S-FmdI4VgIdLE`4cZ9Q!?E{tfo*jxqUWzgQx<$BTUgniO@uWOTCsBgtIV@4Vs-9jsgxV$aQ{088+r?4g_TkpokPLk$MK~c&224a78}%(!0Q_11+L9KHpyPx+pdq%EDVz;HhFWP%5q~b6!RFAKoDJiJcRNGBsUS*c+NFNkTpkz8D67MeQh3nbJ_t!+Z{<%8a5WhSL7ATUL|ll!A+a7{n*}sUm88{vrta+YDP@x$r9m3bTSes>`Ux#-+q13PEj&x^|F@gC=E^_=LyTICVV2y#0QAbEi2>&?242^^a9Bo~baABi6h6Q(JL`1<D4nFfqHYNGO6PBlo{uQU%m$%0}cXmh4OvpXIGY5<0bFleT#=vs}x&C7q<6)gg3}M4@a|z|Xpyh3wSJC?*1{xaLj!;0+c%4WB%hI?5HjQcAqzRSft)mGaO1Clr#04bn?z^p77dgK1I_!ydtt`)2Qv$4tT!O@M)xR=8{6yME?T)=oztmFGmyCTe)PFxSQJa8@smb-O<*0;WOFydpV;w?!vAA@%4HW~`2IXG*KFDw&GbyIf!Hlw6)nuI6NGxL$CeJE763o!C-z;Pm-D2M=dm+!`#BQOtg~uz_a>Q!G5K@M!??j28GC3nq(t#yKTGfW&o26uL-s3l)MxFP-&EjQmNp_DC5{r)qbMC@6TsbWOuImr^dEs1?HTG`4@nl4enU<WGou8uBAl7uypv9a=*Nzc~w_OfpV}_|3OD7~=R^#8i)ned(JR`d{N91(Sx3Stqa5$ei*jaJ&|qp*>W3a^cAk?r4x2Z-spo{R>7Zl1i+P`=k)ISU>fR2C#cnR-T$^K}vRxFh(~pl&%NRnQT@?tD2qoi&cfyj5Cl5@hl{76gV5~BXu@S$J!Rh0IEqi8v%}8^bDkQCJ$%4fF#&e7^|*M0oD0Tz8W8DTItE~tnh24qj>Sv6I1cUG0x|Qh=k}0h{}hst1z(?Y_Q86#nm8n8HI#TzW}A!Y9!)fL_la>)*FZj%#Mh$KUVB%F|FtyDL7m!hg}?5n7Xf1&q+Cw=TYc9%t1oVueT#lH`^Y?EX6BmW|C+AKyUZvFGz~m#7r_}DA@ubWUw?imE4p7Sxw?Tb9>HQsw#OhK4P-*`JuFJ*PGOQ9T{$suv6$Bw>(}KSU6vg?ojHRAwMO&!@$6ykME$=>?y!GZ|bvOjOSSVCF225;o$gfNi40^c0^9Fsc{KAyFYqVbpWz9P0R-?LyKxdA6$Gn`R;3^C+$*Ql-eNGWb(`8y1L4MHLc4OgG)FfaZTn#3%A=yxRogcUEau{?qA^egh)g>P}Yakt10}OH7$$Pn}{13TAz9qts-626&!j;r+s9qB#^pPAssiLvqz&oZu?b3KORx8Ftg9%QHXsqwN$m}3HiCSeJCAqlG!ZKRNtsZpcQ+0+=<V^T&{I4@%S`Z(blPe=%yM1jcRu^8)Cqtu?o(2`EJ;$nCLk0OUlf}8KJ2s?Mnjsxf{oWCz%s#SR^LPJy4}&K4#-k)voo_cHW-rpraJ%q!dP|ia7i=G6b)s74c|`=Lp^zsXFDK3uTkT-WgRCIIvSPZwIs<tzwv|l}2meDx2apoR4@l$W(tG@~P!wPPOffiQnX~hohd7@OK^$I}&&vT}?sSWl^gUKpgmvKaI~i9ilWeeJinm_b(5`#f{Xsp?1=}az}BkBRtcl<*;yEeiOq%?4qPYUVSQ3OeJd*0!e_^)9Y%yLrN;rVN#1}C}tY$q|Q2M@J^kh+>$5UeO<U;L2`Gk2fkL9hfWtV1?HmF3OBmGrOSL#<)WT>!J5o<TdKurgf{3fR^2$(XhJ!Qb1m;FKq+sMquyy=Qa1r7s^YV*$=Q|5HL9!?2SxpcSdv4b^{hJO+PsW&F``v@CFDRDtCi+}?Q~LBH%Q7z#-8c5@?-YhP*5s~&>>%W=A(lh2{WoHe<~!MXo|&?uS^>dbvbUZFJc=wUNJgx(F+kLY>VepHGPGhFp<3zE4c8g99r*F&kLxE@QT;N5>i=fM1)<BXO;UlOV*CSTWV~NAN&6mH-{J|xgL(o%^?iFGhda_Z*s`yZc{n$Pt`eeG<7!F0gDN-eumB3DLWab7TE~8x47?<K5k?5g9t@16l$w?R7C=2><h4Y-s7sKZZS+MPw7pm+d|e@FP$nSOw<uTH%Ob``b?fer(rUxPC8C#U`{1i_eKw|KJB4uta|;_!p!_9_oq+1b;V1{W$d?P8YAxhM3PTAG{qik%(S#hT{Rg?HmhP$I6YPzE;Tq~kFS2=NrNvci6H@RT|<P>Z$0Jd^l-IK%#*UMx1r1>8+O+uI&<aLz^9YE%fq`mM@;5AWa@-b9!v#Ld9k7<U*<-DR~GM?Y$CTv{7L!~xze*9js&A~Pe;pT`JfEUobH1ziWL;)Y@W>iL0t*tGsNmUuGy`0$&S<?aUp;j5j+w9o5eMG%gD~J4epOJQqJKc98HeDUTzk1qK|miHio2p6W#wiX8O?dT6_oaMFk|L|6>=}NWl}aD0qC-PERkto%!><qvF%z@}QsfKGMl?vk?F~D(#kcN+bK3c26Jei93*EpMYom>~fp?PpeDoF_a7u8|TVBKc<P4JYFjB09uD;VX`%v6o^AVkiB<^E)c!qNo&Hf-m1gF&zZebB4zim9_iJHqQ#WuTV4_#B2XOr=_BDgY^(0JB#_ytpIl6IMcGv$1y0BpRWMlE^yg*<Mk6~!JYPBSk{EQ}>{R<Y=Xh;|S|!@32Rj=Oz{2uED2(x>GdV|Pz^j%MJd%QKSE0fkb+0nAVM>r~XCW(0&5c^t<Q<wNo2+*X0v)`%F`hzgDrYq1bNM^)To4-}LcyReg@Z^dj}YCA=nDlatrU`lBk5Pk>r6Qcf?%wz(W0@u)Y;KPfPiNbZP+-0?#TJIH)TDL-!brw?63CJ%9x15-|V3<<<*5VoGcx8wW+!RVE!9F|NQ;GNvN|Whx}B7DvT?bDmW-uXHQfKdd@>e&w1Gcr_nqeM+Yr7FJWW~#Y#%8<r1bjI`(#<RY~H5w)f6J%q7voYf5CKbA0he6Se|T6V~L2vmB*X`SA-_^KBT{57jn*CBi$K!sBGQ#a~GUc4SnMGEV$if{fg&>z*Cf)P#bRbbUmC(PAb&Xi;TJCy4h<>HVzf%KZ%}RCA)js(xohdWfas$5W|ubcbUlqc#H}<vy0MvI<1AD-!;G9G^Q!qqJFqVjMM`RWLS{!1H<Ec!;Zs5XT@|T&|~qb3gjMc4o%DMPu~MGxKt%YPo1dE&tXKcBsX5*jxCRTH(ISd9oe@j4C7K<2JlUKeH4ML9Zyj*yp&pbZ+UjM2AKpZkz=HbEdU9JKGH*_7x2ibd^#Ffw<8U<7<)bG?`Si$s$-z4#7JF40w3Zl)V`nBb6#EgR9N(s5`+r!uOlwE~9CkS%0B-Lnu*v6Zy+&-AflF>H>2OEU8V@iHgE^3Bz;9HIILoqEp*{AL=1ybD;cr9SbtXAFg1gT&PWpW<sL1oZ>=dc9rUsbSVUJ<0NA*+Rjbg>8=n0==a5a)%SsFloByG$_;VZ)62bhXS|dq<Gf^l_+%4RSbJ(|8p`DEYR+tkMz*&wkKsNH$_v$>F@rC=qL|(|5i^MRazH9lQN(338*Cz&*oo$m?(@yn)16rh)eUejYr>e%=VLl)IaQoUJFoaqk!P=-^S-g{j&-`i9oeYTE=ICUohgU=n5NMaavo<KVA>1gPza?gYo{0HZs_m@GHwZ=X^FNxk0JHq(;YfDYvc@aC$AiDWLT*IT{R>$@IPm*MBHAv-_VKM!2%O~Fj1ZtK9~2Mv12)G`~GV?tU7U~FvTjx#HRXu{sQZ>X-r&d`w;dqfm!0u#4mP7LC(1#=Wp|(^2LRZHJt|f_om(r!y|{&SB^3zjw#G}kwWx2ug`PcYK|^>8fz@2AhOrS@Xrbo!`WU#p>KN-jMF1=k<_Wp!0N<I>gT8IqL`UUbzw`T@I$Amtgq3b@r0L{@PMM=dDm%hLq~y6`^<eu6<HpTEl=;*$>P-Tn<+@+vivK4hdG`?iB4Qa-aT~a{ytkx{utxWUS4l8_R^9hFlBO!q*C}l?K4h>Z@60=SFQ4GvDYd_X-e2r&#aDOuML|aDc@G{ikeMh>Bo^SUkjY|<Z(!543Rl!msuZ?yy~Lz#h5vnD0p?Y4H{XYRW>7O6hHf_VfX?ntZ0O|az{iZrS<^GulHNjx13?eCjM7Q$l+L!zt)`LDsnwlYG0*N?|z0*0)cX$ATiE63f^%qT}DQ7d!`+Xn(hT|zkj**FFRe4Pt#MDsBC`k*&Ea77&9HSDWZoyPb2}KoFN>^fGK^cWpF#5LVH>>U0sr;GpyUV&^2?K4m&h3i1V5B-Th}iK0Ch#%=w36or;!pO4X=mjb<j;#<=#`<R_!JixG{7Z)pyz2u=Rse4p5!T2XB~&lC;5j|g)e9V<uPYd_eX9Rh~zQ!r>a<n|dO+eHYfB`Pl;B}7+a6W(FPahmSry?wJh&&n&a=-dw6d6j3-t$3cz*A;6}ylP~pR1REg{#GKCZKi_S4n~Yf+I-`bPElcsN4TmB<G<zRNoOk6Pc>xYx?8f;Mw%x9pS@SF8Vf4$(T||&-mkrVF(*P}HrYXy3cId9x`M(SGlGxRMeL1<AYpSfKjI7?hAsZ1N7l(mwf2%PUT9;XVf8<&${egghKeJ}GCBI?JNVEgd3@Rvfnb=PvN|SOq%$dx>YGPbJN1rqaVKW-o{l_a=)t*jZ@8OZQbG2KN3W~UhI!qHUL|{iIcs6;Xe#i&ZV8xQ!K&jc$;DvGHhs(JD&kOjns+R6(~IL|)hu3EqowFbTjk5x6SA072ZM!4Y{x(6Ifu3IYBBvBlcPd`L%)jEW+)NOE63PD1yoLw19q^MMe2v@sq(aDDe$i2%ch@ge`$WlZutSf2Os{|KY#zb?zXcBFkUStScje==P!8s?W#G}dY5vW&AdA<me=-q86s!?^|Soy-@f1{bQGy$|4L&OMLoXkmu5bsG$<b*7kuPqe*88k{dio*FLSu?9|e~fU)s+EfF&U&IgU-6aF`kZVD7cg=gaJ*B75w74MqB29G>1`HhT~{OCc<`?s>LXgKzXoB(sJ(ML8@|u!)O$sU;Uo4+FC}lL9vh&azG@(9B_66wBo5H`P$VY@pK1%cLk-6U29Iz4D@9s=s{+RBAL{Li($hg+m0v|Kem*ZSFx-REvX{?Q-sW6cX2&)u}M#xX-s327UPX@3lcLvr40DIj*;lRBc_IG1%OFNuG*~3W`DE?Jiqs`4P*gG+Ey#Ld2u_ya@5pn@VY)tBNHrd`$MiW@(UK)3&IK-~Z4I-+uqC`1!oG*Vq35G};OR')))
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

# Local execution overlay; the cash guard is adapted from Arlene.
# Embedded farm programs were reconstructed from the attributed replays.
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
        next_pos = tuple(pos)
        delta = {'EAST':(1,0),'WEST':(-1,0),'NORTH':(0,-1),'SOUTH':(0,1)}.get(op[0])
        if delta:
            next_pos = (max(0,min(9,pos[0]+delta[0])),max(0,min(9,pos[1]+delta[1])))
        next_dist = min(_l1(next_pos,p) for p in access)
        # A scheduled move away must not consume the final return-and-drop slot.
        if 719-step<=dist+1 or 718-step<next_dist+1:
            units[i]=_move(pos,home) if dist else ['DROP']
    action['farmer'],action['hands']=units[0],units[1:]
    return action


def _early_feed_reserve(obs, action, step, state):
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

_PORTFOLIO_PARENT=agent
del agent
STATIC_BRANCH=0
OPENING_BRANCH=0
LIVE_BRANCHES={}
BRANCH_MEMORY={}
SHOP_NAMES=('BAKERY','PIZZA_SHOP','BRUNCH_SPOT','YARN_STORE','ICE_CREAM_SHOP','PET_CAFE','SMOOTHIE_SHOP','FARMERS_MARKET')

def branch_features(obs):
    shops=obs['town']['unlocked_shops'];p=obs['market']['prices'];s=_seat(obs);rival=_farm(obs,1-s);farm=_farm(obs,s)
    kinds={}
    for row in rival['tiles']:
        for t in row:
            if isinstance(t,dict):
                k=t.get('animal',t.get('crop',t.get('kind','')));kinds[k]=kinds.get(k,0)+1
    return ([shops.count(s) for s in SHOP_NAMES]+[p[k] for k in ('MILK','WOOL','EGG','CARROT','STRAWBERRY','WHEAT','FERTILIZER')]+[kinds.get(k,0) for k in ('COW','SHEEP','GOOSE','WHEAT','CARROT','STRAWBERRY')]+[rival['money'],farm['money']])

def choose_opening(obs):
    rival = _farm(obs,1-_seat(obs))
    x = [rival['money'],len(rival['hands']),obs['market']['inventory']['WHEAT'],obs['market']['prices']['WHEAT']]
    return 1 if x[0] <= 76.0 else 0

def choose_branch(obs):
    x = branch_features(obs)
    rule = [8, 191.0, 3, 1]
    while isinstance(rule, list):
        rule = rule[2] if x[rule[0]] <= rule[1] else rule[3]
    return rule

def _select_route(obs,seat):
    return LIVE_BRANCHES.get(seat,0)

def agent(obs,configuration=None):
    seat=_seat(obs);step=int(obs['step'])
    if seat not in BRANCH_MEMORY or step<=BRANCH_MEMORY[seat]:LIVE_BRANCHES[seat]=0
    BRANCH_MEMORY[seat]=step
    if step==2 and choose_opening(obs):
        LIVE_BRANCHES[seat]=4;_STATE[seat]['route']=4
    if step==240 and LIVE_BRANCHES.get(seat,0)<4:
        branch=choose_branch(obs);LIVE_BRANCHES[seat]=branch;_STATE[seat]['route']=branch
    a=_PORTFOLIO_PARENT(obs,configuration)
    branch=LIVE_BRANCHES.get(seat,0)
    start=264 if branch==2 else 240
    if branch==4:
        if step==2:a['market'].append(['BUY_SEED','WHEAT',max(0,7-obs['private']['seeds'].get('WHEAT',0))])
        return a
    if branch==0 or step<start:return a
    product='EGG' if branch==3 else 'MILK'
    units=[a['farmer']]+a['hands'];bags=obs['private']['inventories']
    for i,op in enumerate(units):
        if i>=len(bags):break
        if op[:2]==['PLACE','WOOL'] and not bags[i].get('WOOL',0) and bags[i].get(product,0):units[i]=['PLACE',product,10000]
    a['farmer'],a['hands']=units[0],units[1:]
    if step<718 and any(o[0]=='SELL' and o[1] in ('WOOL',product) for o in a['market']):
        shed=_shed_projection(obs,a)
        for item in ('WOOL',product):
            n=shed.get(item,0)
            if n<=0:continue
            order=next((o for o in a['market'] if o[:2]==['SELL',item]),None)
            if order is not None:order[2]=n
            elif len(a['market'])<10:a['market'].append(['SELL',item,n])
    return a
# Observation-based recovery for failed structures and short feed pickups.
_RECOVERY_PARENT = agent
del agent
REPAIR_STRUCTURES = True
FEED_RESERVE = True
CRITICAL_FEED_ONLY = True
_RECOVERY_STATE = {}


def _structure_recovery(obs, action, step, tape, state):
    farm = _farm(obs, _seat(obs))
    positions = [farm['farmer']] + farm['hands']
    units = [action['farmer']] + action['hands']
    pending = state['pending']
    jobs = state['jobs']
    for unit, (pos, op) in enumerate(zip(positions, units)):
        key = tuple(pos)
        tile = farm['tiles'][pos[1]][pos[0]]
        if op[0] in ('BUILD_PASTURE', 'BUILD_COOP') and isinstance(tile, dict) and tile.get('kind') == 'WEED':
            pending[key] = op[0]
            units[unit] = ['DIG']
    for key in list(pending):
        tile = farm['tiles'][key[1]][key[0]]
        if isinstance(tile, dict) and tile.get('kind') == pending[key][6:]:
            del pending[key]
    # Only borrow contiguous PASS turns, returning to exactly the original
    # position before the next scheduled action and before hands despawn.
    for unit, (pos, op) in enumerate(zip(positions, units)):
        if unit in jobs:
            plan = jobs[unit]
            units[unit] = plan.pop(0)
            if not plan:
                del jobs[unit]
            continue
        if op != ['PASS'] or not pending:
            continue
        run = 1
        for future in range(step + 1, min(719, (step // 24 + 1) * 24)):
            raw = [tape[future]['farmer']] + tape[future]['hands']
            if unit >= len(raw) or raw[unit] != ['PASS']:
                break
            run += 1
        for key, build in list(pending.items()):
            tile = farm['tiles'][key[1]][key[0]]
            if tile is not None and not (isinstance(tile, dict) and tile.get('kind') == 'WEED'):
                continue
            dig = tile is not None
            distance = _l1(pos, key)
            if 2 * distance + 1 + dig > run:
                continue
            at = tuple(pos)
            plan = []
            for leg, target in enumerate((key, tuple(pos))):
                while at != target:
                    move = _move(at, target)
                    plan.append(move)
                    dx, dy = {'EAST': (1, 0), 'WEST': (-1, 0), 'NORTH': (0, -1), 'SOUTH': (0, 1)}[move[0]]
                    at = (at[0] + dx, at[1] + dy)
                if leg == 0:
                    if dig:
                        plan.append(['DIG'])
                    plan.append([build])
            units[unit] = plan.pop(0)
            if plan:
                jobs[unit] = plan
            del pending[key]
            break
    action['farmer'], action['hands'] = units[0], units[1:]
    return action


def _protect_next_pickup(obs, action, step, tape):
    if not 24 <= step < 696:
        return action
    if CRITICAL_FEED_ONLY and not (step==243 and _STATE[_seat(obs)]['route']<4):
        farm = _farm(obs, _seat(obs))
        if not any(isinstance(tile, dict) and 'animal' in tile
                   and tile.get('consecutive_unfed', 0) >= 1 and not tile.get('fed_today')
                   for row in farm['tiles'] for tile in row):
            return action
    upcoming = tape[step + 1]
    need = sum((op[2] if len(op) > 2 else 1)
               for op in [upcoming['farmer']] + upcoming['hands']
               if op[:2] == ['PICKUP', 'WHEAT'])
    if need <= 0:
        return action
    shed = _shed_projection(obs, action)
    available = shed.get('WHEAT', 0)
    for order in action['market']:
        if order[:2] == ['BUY_PRODUCT', 'WHEAT']:
            available += order[2]
        elif order[:2] == ['SELL', 'WHEAT']:
            available = max(0, available - order[2])
    short = max(0, need - available)
    if short and len(action['market']) < 10:
        # Actor pickups happen before market orders; buy on the preceding turn.
        action['market'].append(['BUY_PRODUCT', 'WHEAT', short])
    return action


def agent(obs, configuration=None):
    action = _RECOVERY_PARENT(obs, configuration)
    seat = _seat(obs)
    step = int(obs['step'])
    state = _RECOVERY_STATE.get(seat)
    if state is None or step <= state['last']:
        state = {'last': -1, 'pending': {}, 'jobs': {}}
        _RECOVERY_STATE[seat] = state
    state['last'] = step
    tape = _ROUTES[_STATE[seat]['route']]
    if REPAIR_STRUCTURES:
        action = _structure_recovery(obs, action, step, tape, state)
    if FEED_RESERVE:
        action = _protect_next_pickup(obs, action, step, tape)
    return action
