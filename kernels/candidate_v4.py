# Kaggriculture V4, frozen 2026-09-11.
# Execution runner and cash guard adapted from Arlene (lynnsakurai),
# https://www.kaggle.com/code/lynnsakurai/farming-score-v3-replay-revised
# Arlene's public Python source is Apache-2.0; its notice is retained below.
# Farm programs reconstructed from user-supplied competitive replays:
# Fih, episode 106687524, and yuki0731, episode 106667639.
# Those replay programs replace the original public action tapes.
# V4 changes: safer initial wheat purchase, updated opening/livestock rules,
# two early geese replaced with cows in the yuki programme, and corresponding
# inventory-aware animal-product sales. Existing V3 recovery is retained.
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


_ROUTES = json.loads(zlib.decompress(base64.b85decode(b'c-ri}Pmg3rvgP+(xUK~=A~RW~T|F}AH8Jcig56YL^pI!_pb-QJqs2%&LEl|P=AVeTcI;=z%x^UN;b~QgtjM^2-Ob(Y&#`m<?ce^NZ~nLc`ak~rfBPTb{7?V(&Cj3z`qyusKYa7Q|JVQXfBnC{{^IM8|NX!IkN@Mp{oh}I{<m-b<=6l6_n&|H^24v+|LvO(-<<yR^!e+*cgN=s|MtyapMLsj`@8Jp&;Rd-%V+-O%P)WXQ~pr<n;(ArpFjQh%hNaR55IlQ=fC{;=g+@A;QKG9Z$2EtumAd|r>CEP`;X12|N7<E>rsE5ydS^+&%gfs`c=Pu(d%rUU-9y%>rY?4^X5tKAAA|g)gv#yj-K@|zyA2s4}bsqk-z==+p9YddzsX$hi$&4e8HbSfB$5>Us(UmpX%qFp8oo`-+%c2bMZ>ApLA#K{foEr9{0jupPqjB`u~4^`svGGgo$kDi%0PFo&WN;_isynvss;LNO#*Iy-lnzCGoVkp`AYe?dg~8PrpwSO#6TOZ6sGuIREkao8KnevQ_I9U+m%Px$i5Q&-M8;*E7^!^k{9?#KsT3%->{%ufE8f|MUOF{dD!*w{tkW_v;s2Jn!v@6chh;x?GMR7?k(iFyC>x<1}xdUrqC|G0n8zak@93-ecayI@7$re7gPMt*daGi9ghjh54>G8eN6)1;xaQ3*?3q3Jdx=fa<Z02|a(eGoj*2TAI-9qgr1KU$^;T<O^L-a^_*yevY{Q#4^@5%yyviSA!e-JgnFMGrlF>zwdwh`d`kMeEI38r|<vv_y6?t%in(d>Bs+Nd&Iqell)-E;T3*-@||y<!RFU;-@OJc7a#q)-?P9aTrN+aw<~<UO1F-x6QN~ZU^ct_rpcqlD?4Y++ir}(MS6}JFPJ|k%;fA`Ie*P<hAH;%(s<ubnit#Jd9>%#Vdbn&_T7S=!?Ql;RyMd@meywHn=Y>K|38%eZU5oE%1DL7y-Yck_bujAY8#7JF9q6kab?b8buZKN%1d7*g6R87yMPJagq_RNt1=|z`0UwybqHFsDcr=h(OTvT;r!xkuDXmk*z)C7x>pSM?F;|(`IrBBmd}7$ez$^2@MTT+`>+?nSbH5V(nC%#Tl&b0<}IAwt2-cfrt<X`H^sd!JiJE-Rg&Pk#=uA0z)bKA7Wu<+TImZ#7W~yHjCFzuh~wPF5xH$fqT!kx+o_1s7oj4F^;54Bka{D<jU38>jqHE-S<Q28uji;VQM_QXA7;xSj*QOD8|OR@_&gU^m(1*vtkxn#=T$CR-F4TNc6{!vQ+!8#&$hF*@!GqrT<O=^R%OkrfC_l$pJ1wI-birpH`6I@h<*JM^=_8QG+ahD(E1YezFTGuM~=|Ze-s@Y(jz)%9?`mEsp6)|`xpLr>UkJ>1Ak-0$N3%vd12@8P4O$`_uFgpHo2k@2~Qhb`@(B89yD>|GOSA5t$Uceb&X2SUa2MYcl@Hro?h0-xq8n8TS<&ELl&n#uiea?t4$Sc-z-V)vd(f&;`_E~jFt-`av%e@s%>`fb1pm)cB*#vXQLyMRZS-TiMqwHVCGh0Aoh4)Q7oxVj|q_r04otM@?l^5xmrn8WJObQPSCgq6AKaWtc6-8<SoU6j5Lo^d!_Gl2i{M@H{JrWl&SYPc?o#V55Ii*x$BsS2;gC!&Eh=hTA6(M_&l*XcE)^QBKjBYnqjP4uIJSb&pxW>#(A~cKO3T^5N<Gh3OU|+Zf)p+ixs$qOGpcFcE_rx#1o1gmvJ2@K1in?FMmFNB7?`g-v597+b^F_|MK+9FaJfMn~KE2`+B|I@fY6)zs8sM4mS#W)GVLpqrT$QcUKOF+!O<N0H@J9NgoBH&Z~T7swXiS<7(SNsdBsM6l<G<5bkO@oIx_BJOPxQ44%Vj%54?0_0=MJv9f`+`6cye={R0zwhZ6P_pqY-xU>|z0JFDuIe9YQU34e*5nBx`w{RfQnNVwGKK;D&<?WI|zdvAB)K5t%$aKs}bskxJKk}86^F#PW`wT)vSvrUpE)$GkhqUQ?TK&tHub;g;B>qn_Va-uuwe)=eFZa*ayW)p$?55f{!S8D+5`XW%!lYmg{eb@3_k~OrI{FCV+tfIfmq{%H)-4X5yUDtX@|fsP_Ug%(-ayZZlkuZ?QtS|b*b0UKZMov)xb(6_1N5e!){X5vtXJNw`)-#sDeucmo5)RFqwU48w>)V|e^U6MevciFmO6xOSNn1{OFy<egQ(+&4!pSh@6(2dO*&Oxx?AjGm5ivC7z^l&B^B7^mxubMn4%ZjB0iX8CQ8E*&!I^x;8d4OeRKh*YUyM_F72}S(i~-vYcG6~kt-pDcY=9p@C?Q~0PK);4Z_eYZ0cdKw*P9*2C}%4X0PvhB)L*JaQ!qhvM?X-wHIU9IsJz6;%s7z)lcs?*Tzj+&Be#>jg8Qo+j@^IJv^l9n#M38-YNxN&#t%(ht+G-UhLjJ7`z*mKX`E^MF>fb!W%IH=(jD=2Z07Bix{_|qj5vk6Bx=4Mb+;-XB!M&6>(vBfFWw#8Xx1ovt4W*&n#%>Y(TN^aQqnZi;p#0<PZ>_S#?>uu`Y$37MJr6Rgm~TXFvS-uXVtZG75?GjT+6R?WeH+^G~7nIC84P@$j~qyoMsbxO2g3OJ7xF2P>y_oUwt@69yk@jC(lF;_J8yYx&MgD`k*Gm1%-ac6v9?p&Q19qwsHMq`DI--RP0Cx?h42`#7Tzz4qr;LNr;85?z|T6#IvVSvgSD;~2Y;(mIunoyTAFc02s}$DjW5Hy<9WKq-9us$>;QX<ohT<=gHK>9kc5l~_7l&6K3!gR%_>r?To8pbwPi7Vmx<VWgY%pRVq)r{MEm7sg(8pt^!eLRSFIXe&Pt#;$|mpX?5^NiIH&D)2v5m@=p;_Ypf{ESIk5rdX!a?VUb@Mu8MsXHR4^A$yXn*4eSD_Y%}<v&ftxlFF{t`Y4`P$0*`7rop1N2ayIr3b0<t83&_Vc48_-)o|^IpjjUEW0I{^eMp*-He778fr`|#pdJvdK??9v#8?^6aNQ3e{GGV!Vul-s*VG_sV>7Th1Bu9OGC*6a+*(oA=82inM2kb%VrU5MwxRl^ye@YYy^JM+`?1_OF}z8Klo`Ip%g!o1mXD|J^XDS(u-+_=T@y6|7MMy1&(9vgs2}MvPL$*P^gJd45+K->5@o8I@#@UqwX295EOQzuJ+x_Ws(8NzrX@5LU|mIwF9Zc@e8}e<)a5{KFAw+{2YH1dz3;)fN-R`9NUN0eHmGUki_0B!Bo_V8j>~NMe<CTv3EJ&)71|X%kx<cAo>Xie0=K0M=<V9Jnym)XFl}JlrM(H))GTfJ<MKKU<DrG0qCU7$JECPVLq?Lm(OkqUdI>Qfv5UyVpbb@cBDs4k+Q;Us7#L`YSyjDjQ0`b@A`>|TVQbjeu*6m--qc3}!<_7C_7tzn%z-yI!!WNhb8-DSIwazi_J~QJ%EZ|Rx02W>-<HH{X_dyv0a6Q;*;jmgp5tF#?m)Cgmr!nrOC({x@TSrQ>^?NcXxiD*5m!`D_lh0&qRg;(8hlQ#1-%|?7_;bhk{cz^PCEvQC7h99k&Lk0FkST%1_oSRALS)&s92SArfPhz^ERWjP{Y#yPed4EwtK@9{qaTCIp!>i4z_NJ{ta#LA~5$@4VMQdJ{J*aVum$j;eAMM;*ttrVrcOPRS+wH)t95(ED*m{W9;f#YN%AtljD>iooyY9UgOS}2-YYeF}jmep43wTM>H>}_m05=4|WEa1d=aGtxwj9i@#KVAZ~{DdGYdi^$griz+gF&IJ^Tj#+={2^!r8o>|l=)v`i?rJ>|?KG#{g*r{1cM)=Hr-WRNu!gcB|NP^!^+g^)|>9a0^Ys{9v8MZ@+1DUB`UZr*U1iU4vpz+(oeHVPmp?66mDP{`e%KOSEp-qqRW$V>7QwkcsUfZ&3v*cd~R<K&2dOImGo%0$3l^pp7JOFK$t+#<-VTI{$V3%rkC@}@=-24tj%PRy9Z-8QgV?C2K1df8mxfBEur6QR*O#iOtA?em1X>dFaG1;*p3Xdj06uu#rVJ?aOyuD?fyDNqbKC^rke|3EyK^2N@FB6cr^`bXXbI7hZ-J<UnErs!;IlDMx7Jfdw&L?Kl?dX%LNEH`vG^xBmho(i|ey1XmkxjlAvkq8ZVFxv6l_!BM%>TV_|UL$Uv(guaZIn}vGj4jU4<MzP{7ULHubYE+upYEIj2VX89w$JQsUT6=Q{bSb$q3v4+)}sUx7-zV53du04o;1!g8|fbFB(!%1mu8!hcwhWTRd0uwpG&oBhs?C>z>bPiRdrJ$(?$)b>90z(rnnPO#StQ{hU2iKReetR<l+bgB9_n+$S%HWInC|h;X4dsjJ>E7iC3m*X{vQzsum-c>~&;Pvbd3F5wHyf@m~cY``}s=$G=E3C~wL~g~bHXZUz*+(}+CtdFQ$PY&!XQ(yz+RKyJzd81)GV9>$%r7J{cS*tJpHnl~y5_4o(ifizZuFdv+}S(CB8hTuPjJ+T?g!EVNvpbmiZKN@<NYG$s}7{>;TAum}&e&N`qV2F;z`6w&kj$(Sn+iq77=lDbQIw-ReQvK3?uf}s6$Wp%k;gq1c^d?AjXdit`>`=he#ZC05`Zj1r=2OuF$D*`@sDEpcT^;7F3{|)Wh;Isv@D*mgyJ1T4c5W$FIz0r9L{^48UQ(AI$XHr%0vhdV?Cs|fyDckZdrR82*inZ~oTw4+DU~{QSl$A^QyjWg;Asdsu|`RSlUieXJnteTD5etwk~GWEo;hlmQbUMQtrM8n906Tp%lqkPT7b3%iR!2wz{Oa)o|u6VDbvo!f>)CpA1YO{MOMK&OA|p9>v8LgSNyOaoMIfnnhhXrF|i)Hq8uiniJcCdG|FA~cE#Q8xpIx643s*M3(5EJmIle?+(lGDN9lz0VO%OZB1S;2xJghhu0q-FK|I4#H>V?QNBndYJYBxbK&@!%h$FVTzVUJwZf2H*^}y;J6%o@`aHj`J!G{>^D*73`Gzm5NYWUA`b2p=4RlWJiZEIc+gowwmUyb#dBWz-A-?>NTjWp7>V}XgEPdF&G=fH#;yxXO}U!AI|wY1-J-<Ua1_-({tNCCqneIXz{PgIzW;P3sg_h4{p4|oa2*zRz1%aepguyp`OUwcB-u;9~WVq;6SAtu!M?2IbPHKS-cnJwOA!|JWey>SmMnOS(e`TIs~_xK0Yc4f?~dP!s@Q`K5I)PN$|#dmaxDs<TJMD52XuGBP0xgd}i#ZQtdW6({9f&bV5o5@nMz-7uR!uIv-u6w_jo1AXa_KGlPlJ6@@JmCg^{pR}2ZxE+YPN*j)6pik>`u&htCef=zD{xQ=A3~zAkwbubEEXsf4SENS;H~x$9XvMLGF{lS5d>aFL#U|U`Sc$JjbNbCz|#m!jk1m(RxPs#94N}Zi2;_~+7)ai<HK189ed`f7Su{C7&>mPI1-Zr(KK}eBjtB(?;J8zVmF5LCf79gw%87(z$8fTBr-jgFHdi@CXgDocMt*`B?<wGOxvXqWP+b8XcvMhR(plzyJ!6*+|bum$W5{KgG`YRz~ReI1kfmpSn1PI_1X;O8!<f<vXS_4dve#o`Tfm<bD2SSXcV#wM7Bf{8+3^Wa*6LQ{rH#9Ki046u{_ENITn6tp}p6EFH%93BnsSBl0#h_pgb<)sVd$h!$aQ}he(I;zIXZix&H!;o4wkh`$C7Ip7!N?_h|I3S1456_!Yp36^0-@2d;k==1!T|i^p0OI&E8dNr`rYdI5+i>m;FYE{b$OiHg%~9oy!ZH`HkE%T)ari)`NK$h@@)YEfn*rBbd7q7wiJfV6cI0n!O9D_bT4R0LP!EjbJ_8>W3RkC(Pk*|+R@RPCV-Vti=N6_u_5_OU?GVw=ue3lckm31eklf=@TO51MBs1!BN|feoK<2aTgGL^Ti}9<W~;vNUp;tBAQ5z{*Xi3HBN%otIRx0I`I4FnT*3286B#GUCQC&aF}}Gb%@dREn|EjCK}zB57O|MeuIGgKDC(XeB55%?lmz7oFKSjxrmsoUso#&uM^PXm^rxG=#VWL%i~m*5P9)O5TV5<GZw>;Sf_H-!09MdX4m*F^1t{xkWBiryfYcqLJPQ`GH31yI`G;#kn*iAKwK|(-BI4!l~v%$ExJY>ZCI8R+qW}-Dxr`mAk08kgaZniytn-6_@6%$6XJuc*V*>4LDBGx##(g^dK9(G3}(-SOq7`NC;Pm9M8l$9Jmlpudv9=!t4u)=f(APpSVy4^t-$o?=2&yyo8_b5`+LxT1#bFTgbPyeN<4prYf`eK>wcIVp%Hs7K9XpsetpB4nVYEXP=$m+S0H`TOd>%)0y<o4t#DzC25O2`h^w1Obln68}tjNRmA(wwJ6nLy3zYkgC)vh5(}aYLdeO@@J5qv`UTJ~hTK!Nv#ax{^Hh{jzP7jS6qKgQ*A`_C>|TV;1M2p*41bSB`tI$G>1fPg@lU1fgs0T-dm#SlpQT%Z5Z$qVBD9zEc?Hr8MeHVtGj^SzI4<dfTHuj_b*}~+&md(aLckjfvn&4CJnUt>9dzIdX$X?RUFdrEJRH7bJePl(E%9?80Q3IPD&-8PIHs~PNB#2W!c|AdV-N9gnPN9!j9vu0m^7=>T8b+GtKXH?j!H<!=T<^O3WIJ#{tINrwS^2=%v*J)svCyzaxL;~v?M1g924Fs7f780B<v#&$)|R*qUHI@xzT4wW#t_}eC0%@kj665Yw<nI<351CnI<R-qXpn?m3a})=~JF5%8)m){k{jLnbSfNyUWRu8_X30=33rn%b;Ke7&cDL67bs?@G>#*h!s7Jjp0^k=E4roo{<)%1Slo%DdE8qIE6tHbd_uQR`0iV_#1bd#kZmpK;O<eStEHO7=_q*7S3VVB!ZK=Bl?1DV8(R#@t-9jF=+@<IjS^eQ8)H~YJemTjTwjpIpVGmRxN<+@aDaoMAh^_e5_AtNvGo0pmbpxlKq3ZbmBOglf6ULtkFS=Ri=V##7}WzN~7vu5wHcTytBsIj@?2NV*YC<wCdDy3Vaqfl??ZxmkfI%J8tLl=CT#4Ib6{*U2?XJDwVFnN(REJOV(6#nZ5@YKgP2*<R2^8WBilF1$doX%%vi^yk=Gc_aU42VMVA>LfC?8^6Qi@a<H~KL>MoXq0r!tnjQ0uIziB8!@P%T8M&o1^C^<xi#Oq{cLOTBeE5^*3@RRTHgm$*aO#)ci)Og&a8L7TyXrC&{vF!@XNz*_nmy%1Fx~3iJ|Rll!eHcL_*tR5Jrr;9v043&9h!;33;Fda%4pKilzL}Bv(eL*==ZY>1t0gxzx*NEh#6^zpM@d#h{d}3;3i@&n^Ht><}i7G7Xo5oMgq@AtV(nOS!=X0^Fkk@R?eLU6m!Ekpkd)*$bOP^@OO)frP{^fKo`N<IS7O3vZf)YOkoLcj>9*)>n$>^U8<+rKH~Oa68c4AtqC-XF)Kc^R<qXK&1^Dq1!MHmkk|X85$<cFQz$jz0h#@BUxL=UinGCEBgW_@RP%m&5?#m+h)QqmB1#^06bf(+R)vvkbJV0+9c@(7t<<swQHzg<r1h1Z@FudU>at&K85DhCl?}=qRFcZCP-IUN5}?cVj-!_Cti<H`0hu_bErL+Dx0#xE1d)odMyx^HGAc|DXUQ6ZROJso>Vc|rGTgATtmxvN%{;@$=LRo@c)x?Q&ybnKR2K1H>F_+D+K~FF8u%1HDo;hE5tYEEol+Eso2Mv9b6W=5kDVMv{te?cmI5$x9}^f4O9UhtMi!_<5w!pcO*{jQky2B4`91{9KuwX(0K?=}yv?@goEYoNySHjvc}Q=IgW^42pngkKNKElFFjm>2E~Ln`fk`>CdqLObATG(iV=xKXvc)iDL=({<yr2qwE1OsnzNtN#qAMtf*`6uOgf~^p%q;dO49fH08#x>!TtW6RFwv8rQZvL;&;@%Wrtb&>nCgtuz=y?99o9gnTD4CM5l8DxFAl>jH>Y3~dEH&{69*G&T0YY$;jM?PV(}zWaPNM%6so=`jUauXSFS*wh1%;B5t(w&PzxHw`Z56?PCrGTbx)-9xmG_%+-O-x#D}RWj@zsDWS)zLvTuJ^iZx<?V*<?uSV9LA=Sl3Eii392aKBqdAtjV?-&dDTtCi8hPtXmdH^zM<>tY`+vmfdx<2u&A`?zcBrDngl5$!31BA9$4$4A^M>GIuD!l~KzK~zbpgV745i!OAJzKMj>)-j-<vRX7U_?)4gWKV}Fq}AKsRYL6yx^T5PZ{zf&<fxCKygSE=CS;j>#d&i)Y$Ku(FBwi6X1dxdZ|}O!e#(Le>M@v^i;pTbo9MAnetPP&KvS_HXSE?N9C7TW639E4v_?T^sYQkyv`)wMhD_|ouxvM}iR$-!lMyP9mW)^3NLUs8(sGxg>3bS6eT5Q=Zm>s^+No4s+wb2MozX?-1$036(G_zx?6@go8qyh$$l2vfO-YE|ubCu}!fqu-51y^<eOo>)v!G%dn+$#*8#j*VaK{Pw{l)6g)}<WbieQ&o88_|Qk}P{KVPmjSz));%)cq8+I+Z{lI_b4^a<OQJC@<T?Br>d>OflqNUT6H%zaLBr^*u;YVy{nToc*{uL6|4?DlPIDQ%HArYml6ajGxL7d06OE?pqt&1aQni1B}_nqf;o%+1)%zFskXLU;Chx8ML5?c;waO_83rybqBBC5J}Lpi4}=XT4#KBGcE&ddce3qrN;sdwWtrguz3ngv@uc4JJP8fVUygdO?qvAgJ4U~W80lXZ*IS|hcH#BJiC#~p2WF_osnfe(<~KpsoQSQWMKKJ73$oO`59ZX==%@i;33gNaK-2WxPliSpBsot)YW}5s#9*ke5aGw1MJlLC^E>15873S=56R9)-1|ZE^5mg^0C1b2r8=@rb0&oG^$W{#F{bZmsXvq*naWukv&mW6ii>VASR(k?*x`<tz(N0!%aJkn@{eJ&r38O3s4hhsOLa<pM1pOTSO&XKlSk+NAPi(iy%&DFEKulvhm5wk+K>YW4oUp$ndF-)O->Pw=VkClRg$-R?{l!5MAda+C{JL?b_v9w(kg!iy$8A23t7n2B3;CRTK|)2r*2eIiGm*ZS6`nkM^s~gnj@r&r0@IH_o8z9(6d;@<%y?Tabn-`h~tu3-jg_%n?3=VuhAM<$;eS#DvKoec-@eJffBg9|2?xVw;uJureNTxg^;7vh8d=DHC@rWd`3jY@H{fKtL8x7Hh39L*otXj*r8D{2*=5{&o;der+`=aAG}0sPvi^8mC=+G^Q?Bi9iU~Q%p^5)9A)^kYTy8R_TE1e6RlBV_+Q_s(!R^!R0zY7KTdeV_PMp?FZ%zrzW_%IubiKN<ac9Ulh%-$NJG4<+L|sCr%HEpg4nv&i{3laJUoo{wz6BqN)B+<(Q1OL#9VD;<qSC4{6(q@nxoOc=yo<ZiwEWyMqJVIG1JBOl7LD1$PMi+2lGE9-&B6T>PNfFP!|ruxwji_^3+W=I3y7EOKEBrh^un-w6vIkmzbQ=^D_AyrF+LBnfj-h*c#b)xt0BN(kJU+j`WyNrb=xPXQCYM~kXT6WFh1^$ZL(Iwx8K0z6SjloW~+*D7G2^!LCu{mE=&C{GutMN93n%(aEjl!<w?p7Ox1*{7(@fLlm<lAXQ?c<f*)i;Een#ej;%JaURwRWI+rIPsgDH;@|_+c&cnVOBR{#kGMR)Lco45lfP)>2J>3eouBraJWO!FiaWOqRZ=T?{1-W?TuKRCel`4e-!{Ov>7SeHqW<eR*J0lqUoh9O&Bo`o11A53{ho|w(DXh%F*10<TxpT(NyF-7nyG*Ts*~_5#dPL`}t-9$I1q%E#(fw`^!wgcV=|I3m)WRi>u^?p@))WOypc#WicL>UIoGaL<|Y&j25b7+K50cCm>^hJdKk)OM}|tWRM!w+L72!)2%DIq5d$-foxfo$N6<~e)*#AjJFHm^#fJrqY40BFi}g>2kwR#`ox&lqsi-(hmbJ7h>fC0OH@21ZmRZl-j?2R)J`&_zc!GWsKMLov#!P4L;7}%OTwfwPkw<>Oh%UVEdr_ZMM}s5^T6bpi;FSWnEn2^1tC{_aC>j4E!zMr@4E^NRFE4)G%9tut@l`plbOjwP!%<F(FS&=mQbIj0&&shxq7O<eP@i5N2v8>q};**!lB@W9cyStLAs<;DdU$BZYz%SDm%1IMW4J5T9HMO=g1~=ZOEZ~SKUvRb3h2Xa?)jR*P$uNyCy%BlIW*WPi^OmzeO0uok^G1XTxLgkMX1NW_j(R+_mTiU~I8^wvXsKl+-Zuh|?CmXl1z((?<h0@s^MH?&g%JK5v96gKPHOyc~%Q+K-2QGDp;S>XpOe2Fp294ntvg1gb&dQaFjE-0pX4He73;8VpBUlBHXeDOEC}$9lSl-T*U+nJlLT2i3B|hRGjdgWm}=(7(^YPJ60CrKy%Ys%f;}&$SRQCT<>L3KHWpg8g00o0wRrvW0KmCF_R(-6g<h$T@`SeG_mQP5iWpAIKGOj`cKhWjSb<tad_1G?Jdhh=IVQZ8fUX(|R%|nhnRS1oSLW=@D9CxctPc&}x>l0YV;0?cj{INk%CqJh|O{dD4)&K^oOlwXK9dyt(l%k|r-DUc*f;xetdIKkf7Ar_icU)7*r>&zD-MypVa%(mp4%XPi}WQtx^0C|o!cRa!90GgEew7eH;8#+gX$A(+^R{Ypi0WP8XvJvk3O%*ei7Gg&Y%Ge_Hq`@X_YZ2#af{Uu;8C~ul(bM73am#&6QshHC0lW8;?T;ButRV!pEL{Jb2kWK;IE%(np6-ul`$6R|+ofP98RO=2^s`1bjgem;}veH!ieeN6YQJKVH#A?oEn)SZSsTBGbW*gl7+=EfMMo3MPE?cokeaWUm^vI_w&33;V2kpZ&5jS{i6J+q`3)_1+`yZG(|KdZ==BEuoYafu(f%CuI&C7@n&)g|!5{94DZ(m8kRpeLKW?%l;a+dR5LJ*45+jq7zY440>i%wMLL`_#p6OH=(IX5odhN3w!Z^PUPH6ao{fdfmXT+Hx(2cQz-H$yaPgIB6dznc1rJUM*_L;|0z0(KR3asqmy6NYCUYt1>Gz~gfu-s%ME#>NdW*=3#Mf<m=LK3@LZ;-diuK&r`NoVKPIfGHxE79Rg}xd$y<0<L9>LW|~}sku?BsOqr;;5gh~u!RJ08uBZT4Ut>QYrHs04*{`pfAO2M6B}iI4_Wr(Zfz>wc3!>%&F;q>#_`w&G&y}cLMQuOwJK7+Z^hZ0)hp<ml}YJ;`Sr)2e)#+MU%vcY3h*|-5#70Jl8W_`>CIX))&xCxP;7oLlqiN0!M-mnY>?PS;kZrGgD+>q$A*F$;z-L9VUC=FSp4I2=gKd3kQ?7&2SC#{<9O@aHck5K#FGhhXe2Lq@e$K`8AbhWW@m(~3>4+sr>I(w{JANu4AkWDznaTW&>_9}Tz13wzX2#@vlIcBP%TIhF!6$HXb_kVbdl>c<sakqx`zjS!g_q4SI`SCW97cJ;tDw)FCYarf&TsyC@NN)GFQ}kFH5aywr`5L)a#4{k~EkxcrMyvp@}CJQyl21nO$czipFX@OsK>zhQ$|2gZ)7QXf6uY=Hg!eY4RT6?VJTUJA9^lkcBc>VG-5IxBKJG19f6ubOcjZR7(Uq>hS>?IRD^xDfojreP)<XW1>fOKsAPiwF}I}k=I>$9_6r#mgM4w!E?EA+$IZIb7EuliE-J>eZ468TB(b~@zCuuWk9J`me43Puo<^WhwR)P<y9%|m#bV99{NqclwkcBr7X>&=a;f)Qx&yjoHrO)Rh1$1Ofn23W`0@n-bxo<E8h=<9!Pv@Do5QS6Uvmv1@Ijv6nWH1l7ZU!HhWgS$NOiT4SpHrdVQmvSK+cSLY5)KZCb|bG{^zIPm!6+H5(lvWO%R08$kn(&K&3acT6a-_ze#A8&vfM@rGyV)x?e^A5Ucyqxr8gk8!9FsNpGYO!v_kZ&AwkH8G8t6b-9?BF@A$tnmkczoq-BkH6n+{_B6y$en(Gqd>DCQ>uhWIT<{Pg0V9D=7)B`{@d4l{>zVl{`|XbemT9?rmuee*FQZy{p_)yy;p{R`>MK9d-Z9`9ld?<Whfc^nV$7hu>Jaxzx`U|9zzGg#ltq=Qoi6@`K5S2&CzrI(<Gzsr_CX2L0`O`_Y|1+=ck{({6(0^cD{H7Z}_yAZ%cl&S)FP~cPXn-G$rvgWKMbN6Gn)Xee^uQR;^bQ^{!M_{QRy_H*vV=LZ8@~*!ZD>Dgaja>Wj?z=Ysf*dtT+(Be%5)BVQ4|C(ifcv9Hs7Y)mt)cit-f`ssZ+|E+l+Qud3I#tkOk@XKMo>y5S>V>im^?lz&Ypr&X<V?xj0?M$e+l9nd)=3;g=Oeyt+ybjj}P7!$<>l-GveTrWVZtPUXy@fZ)`qNgLxQgh|cX)*#pYx*p?ipxsgb^iXfy=RzhN`u-V#t+wfxxx`Z^|M5Ho$Z@Y78zKE$NNtbeO}fuer@I^G@#BcuRStrO|GiS!QEwr0<qTOvDF++hu8OcE0J#a_fJ{p>%KiE7k(<aPLAx;(d$xlnKua1=`rpkvNMbPZvCIQd-3CEA0X%_%skurRg2D1=_PYsUQnCac#7gxt<mn1=jLS_GISZnx30TxKmp|?5=Sr2mpW|d|A`Ihm@ba4kX1kX&zWKZ{hTAm}@d;s#M$Be5EQp+-c>~yf5)3HEt4E`DTJ=a0<B|eqmnrHP#6xAj9wOl|r~lMxx=G9CskwY7|MVpJvq2eNn2SZx^!v-Dh=)@OF9*0<6j&-ywr{4QCp57@ZuAuift$hC!wRn`CLn=jASqJ@iG1q#txcQ?c=30goYwhUc4mBWAPJ?feqiB;uG%!)0UxtuI0EyP=V<=?ESDN72C{J)&dg5v@CxIcmN4{)IoDdLDh~5NwS2INyUHFDy!g2G~XU{r1|3E~TW%wRr6dug!SS#Er|aDs8v!VeZy7Dmi<lmK=4Af&H&|StI9)#A{Ebg7Trmx4uuBg!Jy0vm^#;c?h*i3GiAj2oiD4vo3bMku?`8Sk}5f+Z9~z`4HSsk|GT1N({svxmv~^!I;PefR%_B`LM73T&<)kvZ5(DCurP*B^wGQHs&j=5`B#{k5hZ4?{f#<Pr^6e0<x5;_c(b8cut1rZ$<zQ^K2I9LD$OU)5qUE@9vBZ<mHrq(XJUX$^9&^W(ZIr9p#RBwc0-$qNZ%xu*Oq7b|6nVX|e*ha0zJvHVtsClh9S)Zl;!qRmvs4N*%Z>md7rvDsXIHd>j1Q(<sHmjlv!#0Ns;Jnt7!r@BmJub&@{BI!n9($&HhkjB&LIUf{$oI>p-NAcVVG4rh=|8HpPWp5wAK48EF(jv8ZDia)v@Egi?Fn&|fWYkUtYx{pgsu?sNU;`n*>WWGy#zjvnJb<~clwOSE7I^QlC^!o#5Mg5eNf=uVK!_FgzRHn)KA^f6!1|gy>9mETl2}ZC(+B6dVN&lzT@^MCKC}zC((SE%ve)z_2s*Mx;zLq30fl0v{`T_m5flIVj=GcB)&a30M3|O}~bnaHo{|3)>RZqV32Bz$qO!^u-1ZDyQ(3V?hlZgiCO+W2O6}M{BAiJbViDb<^1fg$xG3>3GL@R$%_@I7|9gdbdgl$*bAt3k9Amq@211~Orq!Vd`v~Iea^h_E{j0N<?k_zndAhUBm;q*dV#0QhiL}@tUIW%bnoa%C^k1pU;EuAdLrCs)3nxpJ-U1!2Wgz!!<PYs^Icn5$TM6)b0Gz*)07_9BTnzMl{uB6%PyB<ld6b@WJ&5SI}$9wI?7<Nv-p}aVo*kbill#45$YUSeN_r^x(&27C$mL48bbxmWK5O0+NuV+_WhQsQ$X)ktfJ5-XDKZvYpISOyY2%z7#L>~kioGfCr)UK~@s18lCftgYgt1xALcz_{l-5L+H&cX4_f@aPJ6#EXxk0C#@c~3fhF7D*Ss>{-ibt&w$xP^#e5hR|8O{2PRbiYzYA(6gOqX|;5Dou0#DbyZEPIWjQ-d5Aq_^h!mvx1cnS)uG;<+P47Hc)!P;6sgZ564-29amv3-+5`J43elaO|Z#M@5VWF!?<u1{_TuZcS5BbJ#tp}OAuloXB48>{@hB4CaY1ROS6|^|4n;kQVt|ZM~PiXX`M>P&f_n-*7tj?0;TYAsq@!uGkBFiIi%B8MO3M%S>-bkm*{!Q@^C7vjsf}rm8xU<Kb3TzVIR~z7U-=vg|U|%n9HQKMp6j9pIrI90YUpNFq`D!!>9uPQ-vve@K|>+dqFHb7Rzj5Qxl$#^AD}F$j~3MC&_AUbuou5%UNVj5lJa4naX7DA@`65i`pJU8e}T=g(@kod=S-e?TDaR9`$1qp|;98a0PEL4)pY7sM)L5AO(0SVyuj3xb6oaL8cSvP&E#(sX@}lW?(ajFNu(;kG591wW6%e6EmZU_QaEkfi^3!k$&h%)}bZ+i{-|N;Y~WE%<wf{c2?oBd^~-hKNoq2^=5JGny3-5z*Itbo~d#4n%VPletI4g0SOT7UNV;|R=I0e5jR-oG*WtK)816^ehW-XXez+EiWpxA3e@<J&pD{ef!szNGo$P81;TmXgL9QwsC<xCDd}xc)5;f@JLpI(`kx(_+4BEHQic<>+vO^>D|jNIqMb@uS72OQp~bFktJ!KG4buj;UD}&)P0iAlKQ6D+Fdka?De8k8wIf;<Gh`&`8_h+$qL&c!5xa;y4BAkICz89zqJ3=6ih+Tam{rxg2IY<gCNhyj5VnSW4NGig;!S-tFwDuGW>4`tOSl&ur=u{hGIMeLIXWcbmG+29pUTA92e*>gDBqUEYb3{Q3p}PovHgg+fq!+m1JN2?Lb)X_k%axin@Sh3`_LGpX=h7ETv0*YD|XzAGQ;9&@HxE}^m?pe%%a;#Zj?Yf?HDMQa7KbfEN9*18P>&N!@b^A*GG9t8!A@ioT(b$>%2_`zQwR=d3LO3mvJ2Vi+0voYOiB3+Dy^Ep$%RH<{qoz^1#IBA_7g!u!bzW56MkjQUOd1E&iYiVg<1Ja+I3|;<svyT|G+;mFjtNoD!t7tz*$^+#NFIU<)H8#&&XwlX@cHfac}&-Z0qT!Gs_?;>ZE3pkFbP(u$9Z8{vIMy!>7L?spRqSdJhL??4SP5j0)3QV<xS+?fO@6FO~AIUfnl#^}JQH|V3aPUry{6b%K<L<=>PDsx`p;!;wFR6V6C`b8?yuz5g0V+*vKw;86=f1CsG_yDSn0=Nk~*rlF^lqWh4Ki<yS#>k8C6MiXSE&;RkHfpGXjWH8BE{+Jdq`gKbOa%Bv|A=q6w3lRtErQCbrH(tX!1wqiZfYE107iP;#0*K?X9JtX4sP+Qm#y{vmoGmz5gE<%JNgLUK2NBsuAC25P&|%`^kH}pru!E2Fsc9i;8yYX$R`CtAqUfDVf7z~)l$CL+kuFkilNq#H~h^}tXcnZQkp5c*qVgxD+7<n+7dlT)r}rKX#=+n-3-0f<c5F3t*|b~3ixY}ojoK10v?QZH?MUvOt#bA3{bp8+&ZNN3Ndr4XpgvAoT10fgS9F~Do%*K)<!?wHwEIoTs~}++1tF(9y0sK{tm*`w+yUD{v*)LaO)J}U{oh*oMtwrJyt|$?+mWYHuvzpNRg_t4skvgWz`Ousn&rV6-BA)o<vTK8amTom1s?IC!k&<#8?ftVMnX_oHED75en=p;UbVneARNA+rdL}7!(+LktPy@OwqhlE4oz8L@urC$fRT;BhMdT!wDk23hMR2wI+^#kzi2Xl#l<4siEBrD0-(6W9Bo=bEDaG^7C|Gm6d_4lm{j1Qw=<fdtxoDPGhiZqqfy;RQl=h4?zBCR05$pIB~NkSbYt)e++wKGnj+jb}!)@0Nj5xlrPoHTqiM(4ZuQPo`&qgu}iiP9gFi(Rsb8t^oqCLt{~3whw61uP$eY!rTt!w=Qt3ceEq{I6?5rLki5`7N|xA*fT@d{C{6Wk(2UHd@&=AYX$MjN)}*yM%$pXfa1F5C6d2(v%(`^Ll;Z8&(x!B}1saL03}d{cBR>$Vv>*gD+SS<G&m(r5Q^@v~RBEwz4%;<R4c^lvb?mUb1%4+pbnCy<5OQLTlJq9E#`JjJMKVxKCk7;GmZ3d!)EcFR5TjZrFt6DFy2h4w&d*f;Yzq>#Q9FQ(v2;B#10zzVosR{tCO1A*`eTdyfpwN9!Y9__))%k%VLu?nIDj=<J=(HiJ!C~WOhOJjy*6o-yYB6ZyW4Z+8bcXqav<xG@8K;ClFPY^n1YU`2`Rz2q;*7rfUIznpj=#qvay30g{N*#N5qbp=qPx)e3^kR(bN$~Jav8J<u2UJED7s@)j296rcK{Yw~+!5G0atTFnDPaYUkD9pXD}g#=ok1^OM`aydDS<V`0A<>vKfd6xzOXj~p9mq;1Cn6F;ADP-@SC2{#zFOMkyQRaFydzq`IMbDqT8h^>$UhDrKDKzg32Fdbpv`=Rc^;M5-Q5{$9U;pUbnsf%Fi0D`{ugs4@)C&t8fmTE&xNb=bkRpe?$(R4Cfyvc^uTbE_y9@;On@Obn0joR+<52)?Rm{)a?$V#TFwQ{HdMYN0W=u%SXu;GasjZa*uY0z&$ATNraBud7hn-16hu>m%drDlQ4lvRZ7>)HMFela&W-K6amVa_DqSCn|d4gUJg^_kzGNTHliPc|qT-F5Z*A+by%Qi)dJpb|cWL}4R`0QFcbP$<Il4jRE*?IAjNY_w&%uxBF(yo`oWk-GEgKMESbK&64F5ttff9Y3sEW)V10lzkHeEIYI-*h<EHvkp4;%u_9>l~^zo+gfoXCIzBt>I6p0<l5djWT?br4Czg-Y3^;Y9U6g2klsmTdVF4<vS>{eHEi!71UQNj0u-6HOC!hxKUvT%1XHZ`3JZ15`boH<ud9WdV(kZ+A|HUmmz@ZpQ2?=0qND1y8Ok?edMaci#pCwmu7mUYn+NAIgYeKOWEY5Ri6l0N5f9`N-(C9gFQ0#`U)AGtloN6+{L(^YuLEDCf+~p-xT_?Gx;Q|2T*gyXyhnzIzAp}u4z+#n^7nK91sFGbwL|xX4nyVa%lGaP=3B2&=(X`HfD<bWL3j>a|0>L#GO-trwJLPlw(^n^?FRJ%5K-1iLg8E#>3|Xyr@1<|%`tDN(cG7*`Y#rFyU&q%YZKJ+%SKA2To*(q01yDF>LdcB6IfQZOjM@`uEtw(7-Tj~`(hq1ZK1Mn+4HE{LmkBU(4H&OTm$T5fuhAWowpVwb_5f~8oC6ZZgL+q&q@l!fd2v;KH&};M_Y($ASOIuyfg%8<T6(gb1#6En^05hHBLG&sbT?Q3Gra`b~+3QUA1GxjbWTyrCw$vjs&R`W2G7GEb>IWxGIX^-GB$xL{HI5PV}1>Ix;UhvvC|{HePvRA8wx00Kd@gB<E-daS4V@<t44d$552K5B<k?X+y&yrb513nj!TX={sW#!^LuoT&PYxkXS_{y$?bIjna3)G#!g`X+}Q23!J7Sl>UTM&4-Rv$(7YfW#FwYbpg85WLPS9QE?$#-3S*yT!t$y&0CMH9$fK?m4zB`oT78j^BpNaHhN>)NwKlsO_q@mt`Iq%iFG(|A)H=ek(Y(p7k$x->+3#op$zDEc{Sc!Mof7LKiwq=0iLvK%Cd@(Z)^MLopw!CX7PdeJ-fxSRP-$fDF{;m=Pw<AXu-}tJHfT3VUM;Hs5quGk)Iv-+=xojmUZ+CD}b38&Nesb7fh>&_noUws>5`n@u3Dwl*J?rL>q*Vlbhj<Cf)Q4pj`~Pr)p<c=TYaWD4}s}Z`~;<O_i@L${g6e2%87g?Q0qS9*gwd+Z)r-n8D(oO2G+Fqv7{J{L?>6w*(=&WB){GFX{6Nq#26XO%iA9Ize$<QUbNWBL(YT4K|)Z%1DBMHx_1B{IPl1%XmBJz!lOEBzU{f_3n8%e8+e$|1?|T=Rg4F{h?LL8BTFbWo3@~<<Etyj*iD3GT}1CZonA52zD`PR;9HRR{&POE2|xqkdDu-goKm;-G=-Z$c$?X8L*hQ>P%HP4B_Qk<k@IRPE<H1yiqQYItNJBM;ww*?PNvE^ObX>&yLE<JAnAgiA*7lWuVvMdzi<40DUt}P!vWBz}qVGBAnBwJX4e*Z({p>4@@(sg(P;DlOr^kD+bI}yUmtC!3;2LoSG%zw=v*lV&D-gdKw$Ut<cPc9iBZSElLScO5Rh#gC%eZgCyuG*Yd62Z|(3m?ly~WMJIs1opZ8A@<cESvGXjP!>~yNCv`{k1=+xi>G0z}OG0AO5TbHaY09E*?ElmNNgNt85D9X`T_LPm0NLTqdpU`!>4ErIpVE>}#jQc<!ZalN2XpDfaWp4;hpJhlgA}Vw1=on5;>46j)xRQO3s!k&jkO)Sg(k%O*G_2FspS;-EN&_p?n5sb_C$8v&gIQzYg2Q$qG!6~Y#CK5U4@klgjJWUspc|$4={d=XKlzoR<OtTCyNX4I=7fhMRIw~tOV{uHt)lVP@{yf1=Zx&DPQDZZFPt+UMfSO!5uX_<{5Q@pv{JP57jbqOK0X&B*7PN!ddSIRCf9BC(RjDJmzfXgt6h&FS{4baM|IW=F@i7WhneRwgJu-<<d2K%7<XO)w_K{l(dDx$i?upLU(&8-sEGm`W-to6N4A>>r<4`q@gMG&VFX2r!CR%XBi4U?vsD{L$nby(hffhL+}xcb@RbZ#9TI|h}_I!^8PLa#KMdOo{w0S=mfIXXk+GuK18jYI}Ir2hH*f{!o!gLB<bMq78Ogii^YL1g0*uH2GM0rLr$5(65bq#Z*<pNWLmpaPqlr-?ZYJWi^N(JXcl8ud}gg?t-G7qWaJ9Q=%pdA_eUe#*G8vMYQh6D`{lj_t#uV=gU3dU(Mzc2{q`ifkR1?}-r7Z!JnASE;2Nw7BiH7rNwYfIsH9t|WecJf9}h|ED?8y$WK-2;zt}P;`obz3lsTv*m0zLAo+czfm+KuzE!$a%$@2p;aZXzVp>A(8HSY)_6=RK9gScf>m>$lOH3X^3AAHmURp(^5VP#p-#XXyOhL6t;UJCJk2WOulGl{7z;=j`2c|f%x^-(qODSlL*ibx|WflWK5C=NGIQIO`g4749RIg0!n#%(MGVB|g~Fdmi&NHUBpP>CXH0Th~e1{x!!rtb262$+GIBAo$-$*XvqZP7U~)|Yp0)wc4G-WCVNd%QsXmZ*@J;%8v2vO`@+k!b^ya%A^{uFFAOl6}Wu60&8BVaSLkqCt2;75Y{-u_Sy`doo2=P!O{{Q<e#Ds+gHs>`@q$=f5{{I7YaF>|<b}CqJcTh^L?n_DD?M5d<*R8Kr>_i=jHKfljq*pBN&J)|p-$hFNY-!7B2)yW%GfCe*Zirc=UO4_U?HNu=Q3{cb5#eNh@g`arK-fjkSf*C`@0<({DyG>G+O0z904iazU}Na=H}evY`&vW|!kQ&k+dSMA9>7Y$|K{;m{j#Qw$vnhUUm4kpf%*fkXg?WEy;w~RtcDC54bE}d2@qlKTK8%S@A`$pEqK3rx$)KSKDtbg}$*VIeResLq(QwBva`9zM7xK+~SyQPFvv+aYZl2Qkw6-pOf=pKC&38$@NKtW}-Xk_p?Lp#Zy4pT_0x4)}|+8K1=YH{Ai=}E~^A47R}julPFGWm-0=6KjfL?d1@oHWdIwO8KWb)Ef`1rO9?Ff$h)RcbcTW1;-?)MtUFVnfbqLtHrG*h?jlcQ9#<g3eNl3^{0>j_VDX*pFe^Zc-D~@A)PpR30rEuey=2D)^=4E=AM#G-CP+B^2FYk0iBIsk*k`zbiVUi_Qz^fb63y=4{w;Q^qu;Gaiw%%a@vx5W8P9Ng##YN{k*nTig4#d|GBf#Wpq>{602r9MR#96Y%?s)uF9RIl>jeF10dl+P5WH_FlrqV55Mc*xac5DQI;nfj)H7Yw6@-(F{>uwueb%SUZ_w$iKYK_@{qAm=x-JkfOw1pUgP>adm<)PwG`#<T0j@?(WtgITsl}l_B!5(5KwDHn<7kn1KcuvyVroP?)p3d6HmM(@VehK`Aq6K@suDtI6##pbqN}UcVudpl1^+5}mZp`0i$02HNz1ae+#Y1sZBmA9!K&6qaaXqL_E2Q#ryWxmBC=+WrQ?mY&D9JBi-herXS3s!(}$Bb7aga}PTs%Y3F;D&|tR-Jr?9@>46+xgqm2wq()wAH=~!qKDv$(F1S=FFrmu5R<5@`(#w7+=BT|C$9(Csr6B0kP#oWs}9ZE&_k?Ql&f6SmN(>MgDDVHRy9n8js$2_q3(z^W6m$FI#IFx;@u;AqN*sEzGy*ALXF-DEYn)Y79ED0b{IFG+#R2nXgn66CeBdLf$%>0h{LytO1OUN<3Enz<1!aPoX}okd?01xlb0i9H8RF_KR=M+Qyr=KBo=O6^s6U*EWWI!Rnj54&PlY3Uf<ib%e8FZ5gr#oJk$-gaM%q%6=A9<9_$cem_&0v@#fpwm24jESD6X@0A!w(?5%E`LDxO%aH8dpat5~`4OR3DeVrEO%_*28d<Mk|ErrShA4`Y{lRx^vfxUP{Efqcj$QZ;nE2&{+JmPXmu=Qoz*?LkY?pVqUzHit%Peg%$ES@aZT3?378`vEmhXMIP+MfOGAej8xYEt0DdWul#H7ztwyZC5KU9J*=5U!_~n%bt(jq4!8a$~L10oD0l{lCY+Ix<xKXyJm(b$~1kmDb0$N=Vxe%o$EiaCLPgc5ak_1WvvvnqiOiqczHDZ^%xZ9uh%u1`nP8>nh=JC+huKa-u|2{h`V+8E=P7k7C4cQIa0gwiV;cOyBVCqYvB=y+3yc2e@%A%c_~mRACG55cspnbt*hUk*2u#L9<^t`GaBEw!H9BmAuW*;pAB4!WK*iEjGUs7Ca!))oju=pcQ#T|87VU=Asa*N<^xKU)q%rxHGr)sCSbHfd!rdCVY<;Rh1^NU(4zl7;1D*v<3utqL3&l6eq4#z&`2kfouAc*~U<wE>Me>+GUw*3!f<y^JqQgfnBptQJVp`kn|)weG%~3!BQ3%GggZM6^nV~6s@XW-hpxAH#u)0H!iksW-G$1Zp4af13jp@k`g19BvsSjoVER)?2O=WhoWJaGOk6J*W2FRLhITau{cent-k&$09<G@QnqcLZ`G_6S?xvBOIeyQVjea((;gV2${uak#Y~i=xedv2QUar?$ayX@-%7Z6iZ>&|k+S#m%><5>4NzOk9ftRpnSk%i=zbSG$i)^{$qPddCCQk`xwy(=JS@Emg8hjY63`hfRLQgvfm%*L#sGO5CwZ0zwZ+LGHLA5Ev7M${S9C-DVU`2gvMP`B>*W0MMco;17r^TWs?0|f0J>nJmZlHf4KehIF|9|F*C`JnVSEuAMUR%KcuL$<?diNNz2m5zWJrH)ATv>ex7TM~i?@gL?HHGYNoAh=0;8CWEbChYQt6A7kOk&}$uk!hW3Dm#{c#IIuK3{g-cVb%0a)I56&R=>H;8Cd>T+A}u@omWlZT)xYUrX3>`X18K1~JUqRVsjRDb)<7$=WV>&r;Fg#&~`!3#Uq(2Rm~Nu^T8FC*Mm9OqSbXq$>Yc^$MOiz3gFP3GE=L;0?{pDgEq5On3F%iyj<Q<8U0ekdi;Po<vP&KG}+Fp4{qF0apq$KW61N8`=%+C{l*(G9@ZV)bkv(RC=PVdfF1Eqc+)awDdX25#alAMxGIDN%ji2vY{v?74Y45*xH15Bp?}sPWV*hsO<;bEX`I!tMxEgTke75=pt;@78R%);={Dj<zIAw<uGpWJHhkbPv4&W)d@5P74mIWrYosKg0&V6K0@)pM#zDRE0`YEqPSaXuqFpAzn<}Jj4_v#%BckyO=jIu~20T-?~fI4*|MMfX|R~2-W*0;4+%{X%jz?E8raKY2?as&@Nf+gp6n;J&O?ofl1qHRHvu)WKJ|2j#&xlS)kG*w8C)tiC3Z3EM)_PJd)bM8Eun{QcQSqyZiE_A$5Z^s;6pO34eHV<6R_8UP`=%n_O}q4ljP%=h080RiUQ234xz4wNiN@^PZ)BPG-+ItKy{I^W0Ima44#@V3cR3>?ALM+AxhXk=R2pu@U=~isZ=lkav1=9(tIOeY<9|U|wd9wh{Mzg`e2|!DISMz+O<^G|lGRIZ7{G4VzLirPU|XXg0XM2kxs@$Wn-)AP^v(0=Qf5pM5HnSc#6g_M$o|#yhCi9ja90p(_Ye`1@t0srdWcH{PQ%iNlE1oXa%peVJ1!^e@adxcj*WqjHUqnj~GeVv+iiO@-)@PgR=jem4%<hiM{i@YW{C;LjJf_j2|>Fm?XLhn&q%8-mt8Af*H6f4Q5N5g(qpQ_v&~KdIlol7OqouddC${ITUM=evX;6s5QCY-iHm8Os)(sLY9)u9PMk_4#vdT)GWKb7J0xxf5zaBzyt~mQ1;r;r$LkCB$!rXw(L;RGEG?^%Z$?`VNQ$K3N6qD(d6}^h75N&pOtcb2@>?=RmyG3Dk{^8(^}_I>!ZtYKwfl{JF(P0}Oyvlf^h~O)&sdL@q5n{^@cLTDAmS%M^tc%{^0dqgGMXV+X)-xV>Nt3E(v3R~{Q8x0Kg-ag-hcV&neeH)kg{%KRR(?8n{ORJ`rHd<UA{k2#Fvu?=W)`gVj)_Pc6Tq<r6svp1_(&^IfS(*N@7k3aqJ_wT=a`MDI}ZGa=XbJZjj>m}2hwPdUbdhnpw{9Y(g3?+hnUs%{6v5mrUo1_O{&WMi<1vSKxmL<X*IR&x!$LG$KU+f?^zQYcHrftUY*0*h%^wo(c6X?)LUhv{0rt>n2`rXXV2w52@%C%2XwI2C%Q(76Q$>V=Dm!F_RdhxmJhVg#`P{?K}0xqFikRV{<1=-LbFdgV3*J;W>#_M$t5Bh}l_&%?o7hJ~5eQU)Pay(u@3Ty)X{UuOTtTtt?sP$f!TGMRb6mzN983`n5Fk|psw8cUbPb{W5&`~qH&S(^k)p(dtiCqkfFOmlPg9OlA6s*m~z5dhWJ;2*J3vzb&O!puQWw62`s*`W`$D0T0#JcDRrmm=#2zJ!t12S;_!S7P=2X*?)FrUUmkLrMG3=3-)n2RH?yYf8BVHGXO#SMe!a^bj57P98V#_AK}vX}dMQS!A?7m4Gc+hxjtQmrhZQD|T@Zj%n#xjV|MQra(9xhOpJn|>+5`Y}pbnnlkqWzVK6YRNcnFtDmBL+F`g7)H$evgEy$F1%L09|%2=_|#O6x<w|GDUA!@J4`6@sFNfEwexNEtbC96&o~?WGRpP(Mmw*<WnqLYLx|h7jMr(91ALz%GnZ>NIzq_sUXeF~1{|F^&iC(_P+;*J9O^fy>J8!z&(f=j9ZNo*$|gqhUu7QSP$5vmQ{0&DqcPs1l<#X|8ZjvvR{untiECKn4*-8l_fsE#zuElP|DusQ{QyUSW<RD>36XL#coYR=W%kVv?STEaulf9!AOHOMcia4OdaX@g{razedV2cVV?TSZ4FC33b*1*|)08`U`{2t^GWat+>!o1(^&@}#wa7h&4uXq^ZN8;^!ME~D@qU`4=lrKhM&D1HL)L=6csuVYFzwGzKYjU&Fp=$i@d)1VX)oWF{ARN{)sXH|R-tH0;%Ug7^3*4c5GniUd4R22uPEwWsjT?<U88Q|aM6W6u`{vpLj_d;tnk$rne)#D@fr8L%CSdoYZFGkB79Gr@5N(Zr}@~JW?JvORr>YQ`*QwU^FE~P7bT4wOuXTj!+h5pZ8yell+oR7LSaEo(TK)`p1<3fP;n(KP3X<V>}r@&>I-=tt__?b@;25tOl<oUzZ%@wsf>FIZ<6(=tu%2J(V_3~3O_#QMfu$`(BKFoO3VV6V<!z&Yiq@jEAs+@Z3W(xL;P)k>2A~*Tr^tJ8_(%5hg)BBn_=di+_UkP@<>ag-8Qq##@I;TEsvOp4+gi((%S5N)0O4c|ByrJ-u73l1>WJ_g@(lY7V{|+o*4?Xv7aMx7E7Kkc;2M6h~HP*1x)a1AfQUqJ8BEGXLC|P7H;C&Xf1O+EiekK<(uru%)vE1H<56swt(1O<4_O)06+M$rh5-5KYJZWifz(7uxQ@G>D@5bWX@Enwzc_6Rd~45%B6W<;!A4WB(U<$1kd0Uay|UQyzFbN6HGvc-`y*PaFdKg!!<eXK(^H=l2|{@sH6L$R7Kw|WdFO*>Js7Y^c)0Ol|8;g2JafqH0&@sIT~NP-!Tk>Oa(T{(vHu|T^f7nixNpc=!T|Z<HG_TLl6zmH}^)&W~<xzC9+AxF`0(T$Oc+pg5GySBVW@II{J^IgF|{m$IK&IcPw+%dhh)Ue?0X(`p_ZR81Zqw2SHv~ln4#5i}L&JwGmxPNs(*u+817%@t}ztmtj@fZr#J&t!q?r_DU@|>KFt2U-7a=&J~H*o=OGfLx*pDpEL>S-7jZJ4Ak-vYLyb;wOkM+;+kh&?0O?>E>y6rb$_-ixZd+2xSu3N7}S**h&^((j6H%ekqZDT5ijy#U;DXQNmXP;Q*utwxCcu%6iRH&S6C(b8fhM<_DbL94!oa)Z@dL$DO2xp@)Gcz4A0+;03PPqEY5?jmC2`%zkA-@85_vUDgUBfGh~wcSzgT$ph7yz9rJ3ne>Ox-*|cGer+Dl@o^sM;1#aOI(gJK6;94i4tG?Y#EfK4fOMI0&a91pkU07A%*uMBS__e1|iiaD8Jxl<)Cz&+!N=@JaoJQ*;eTa3Icmt9fCovi0Y7@M`iCuJxwaq~YceNbOAek}}HyS+0Woa0EH4z;(#;g>7bUj)+j!!kw?e*9A9#(W8mzH7|V7A5a^Xkcbm-c?|Ouy@>9an3$B6f7XT{7tR2h584DJcb+&Si(4M-Hh>lk-FPMf(gwL|HnB7cLWwV28A6B>I#7Pp#$SjM7ldc<-bAdRP4LjonlmC-{9WNn!$%f;IF5`fCH1Xsyh#{kEJ}$8Q<1ZgJ?`t(yN0p6jZfeCZ8L*)^H;HFgNh1O}ijx6mdN4bYo@+L0=5)uusqNs|)EntKRB-}YkITQiAP{-p3h{T@3UEp-UnuC_x!?w>)(p#ukAT>eNW(g<nYbT{dlG?o|(=!+#4*yTZH=X}EHg|>(fCYg!SaKv+H(h4}$<x(GAz^Pg~S&&P+?7cKc+2gv-gog;>onW3CJcIEL06U0gSz>4wHuW%A+kZ7@16f>2v)6Y$l3XbqxPF=$S(uOa+KVyloPI-jaW=8V>Zd3dS3cFs#mDcBjnJFhdXFqUJf!NH#xNn?Dg|E8uDA?`)oasU?A~^$BrAUqS<`Y9-iQ%Ezio*=2sAiZ#AvBqU*Aw2nq&hrr6g8i%KY#EL)5x89%!9|<Cz7`oDC@U9gZJEeq{5WboyM}$%$2$r5o!~*lBSK5yK)#JQJHnb>HZIrHn!%eWOMbq+nH==KNErJ&v5}a6G)NrmOK;V_jwiD<QH%*}=+b9cOHy^n}5O8si?0v-mo$!dkxb(n=X5QDvH7lbzm;bLfU~;VAsu8L94sN;i7stnQZ}#6Hd_M6dn1l@Lu<qePcxFU9_w_R6FjNRo~cyO7d4m5!aqUv#bS_gDo=;p0;0uiIwuDuHrHr>%;pQc<(YXCf}q^OWV`R8}1W^Z_bW$Mk<H={&<esCz8XTW<<uFFP=oNo$Ry5PCnk@_Pe<_FZ5$$;F3J1^%ZBQ}*Do?qK$USa>X!*}|qKJRj#DT4#}=KV(mm)!OP}4q2A7$ebdQQdTmR$=pNkAq^I_J%}{ORO|~?Qe62Us^QuZL9;yS$0R~+m380>-e4T)>B&&DSFJ$`@KVHB8P9Ot4?u!UC(xm499~m{q>atMW)NQzAyXf1t#WHcS(_(jMicFcCldp0R$wFj(2=Y|OZpefjT6J0bV!-uYrO2N!ejY(`aXXy@(%0G;@CA&BVd84gz!95<LEWB=i~hJJSGAXAlSWRE>)~@*RCRNu*_+s^w6fgsp9<>n3m8~fOQoyz7Q0s@gbjcP?rO_jXGvV*WU|-^S%e?DzQ-cAgxl;+n}bEFD`e`ky!LUJ1(>3|B0jwCuq0JRcKf6L_$S7m9VbBxVA!zUE5Z()j%4i4Q#u#H{qI^r7eG4UZ-I^wD42Z2RCX*v@B-GNYXc&i+DvZA?71?5qTK2p$bnVcaKH;*qjvu11&MDs&@^_9SclkB8MPs4f`6F*viD4`e<O7lReFz;&qmAFFH;~VP0kC;`(!RNW?4c5tBZZiL(!GC9zSyEs57ij@uS^Oo?Lq5pe_m>T(C7HM)dyOI#ue`-L}^E@1beF-FtQmX5fhg1T4ixEE!H#na$(dM)VnSi_h_x0Bo`fp*$4P%Pn$1dCYCy2&%Fi^GO{y{WE`@{%@Gtjal4HNMw*n+kl3Vb${NSj{fuIPw?mth3Z!$6&OXqJKjhya>!aR>S3iiO)p@nwVh?S$H3ko4BL`m>638K^4RbVD;rFHw(mX)fl^amKrM6^W-=sNM~EeqSv_dC4x0dNQ~~}lqdC6z!A+0>b+yIz=NFuCV}LOQtOko;^HsWABdabeO|mgUOfYM6EIkgBo6ODjWOr9Fa3VeK0DZ>1T7PaZBIEf3C+jo=&85rqqS1#3mIe$1>r;sKa^^8ULoXCdWTd;r7HhLQqiz|KuTi^xtli}rXqlx4e*!&s*M5&3Onpo8x(T)=a0u%h<A0iIr5VHgl$Tg3?R6mDmKPY<TyDZ;F4AwoiY*d7yTr@`O=P(8Mg>Bs}?)%#{%!;m%OQwgaH}pp%XJEakmYu7CXAduU<CS_g}vJ+(c+JPx0t0eEU41uDWtURDtn0D%ywPJ(wM3F)x$)(+_S{e~<i9AQ*BmZWea`fmkl(i@kM1Vdr9~edG;*b5v{A&zzKMimtXMf&0q9Bht1+6H>LKM_1awaYJ`QuT{C>rEqJk%eewx+hb=BiLihNqn*xc-3*icbT<POFA=v+X@NrAoGRQSt`=wLar0p9ijj*GqOY~lPxnoMfG?L18)x=5FSLiu{;}VKaP}<&>yZHobTiyKg;*HXO&X_}jd70^652b1E3?f-yf1R3s<cD2&qZ3bLuM*=U`Iufs=6nUW21)B^j9TXQ``xt-v}{Q!)@5nsy?Soa&d$L3rjc&<P~4FoaT1$kR1jk#$F_f#3)lVGt~+&RdbO`^ExsqS=Pw&2iSmu$ghHmeQ>Rb<6k5glsDz$!D4D?Hv@{^X~dlQjPu-hHl6%D-B)F0AS>lTi~7_9591zL3%k=8?AoYpwHuXwdi(>BKpLe$Xb(=@tO;0OgYO^1p4bfLV7K8*I0pdv9}Oi;H8a;qjAH}9kQb{VyKwB1FGR=Ue3TVHM=`zPZMQ3kbNr!t9TZpzNq%X+SK~Pj1Swzta7xWwdJ`l!w2!hS_9kHJ;wH*deH%0*^Qqi{V^P{c)W0=pt`74ihALbGtTzQl_zJVG-7uwiJGZndo$i4~A}hljFX_q;1S~Be0gZMw_V)9L-DVZCy(QIJ?4`r@O;m^XG)f&iEN_9|$qn85?=*y*SfeDtNv$zGo_CQD6w`?TNt$J7&m6T%sUgIu)(OmOc7U$2<(>316+qj9L~Ya#;9@LYPt3rGlxgQ<!K=xQ50xI-BA;NLrHSx~^|<xLD}LAyNHGpz&DM{$j93p@Q4W)E#7^%`8s)BgyW;NlT)D<j1{xj6g5-O6OM~Qc?jok3qj5sYFfNH5Q6eBq+$1O$SD|e5Aco<oo6`}sBW5}Zo-SWzpi?w;#1U0p-*~wTH#1AZdSG>qiil|wxYK>4z(Wjk6`c%TnuOYWHTY+_t()<$s^0wMHZ-pXLd0O$ug3bE5jLf^@7yEjMjC0`vB1R7CmfX8b6~;^#_iJIuTE9fRNC*hZ_J!0`8HxNq<~?Pz7UX}Cn`)w*!O;@doVb)2fPGhY;?G}<w+_d*gAlquRS4ZRq%;2v8AQj5EIgTc19K1no%^J%ocC5VfEH!-MEKl%q%?K{C%Ugd;9}xyE5igT_m!SscNkpYCsX~;ybz&6*_EqqQ>JBS85t`ToA~M;wOoeG3chly?<<g&19)r;4)<uVf%V^zrA0~O-?sydqtQt$@di{o^XS|esg{1Hz-pmC)AS>ibi)`{eDO+lZaKK6*#Db4<S+5$RR*I77G-L0KJ1o@K$?>4jvnAnJ(<v2m&voAyg#qeEN@qMleum;AsS=Mp?%XtCm>=4ishI!~n}a?FzP%G2yI(jy>~K3u+}63<bAV9EnMRXqq~KkutlscMcgU@ft&VlWUrLTWp6+U=pNv5}6*qm!~vZQ%4QkI|u=e;)DQ2rtQ)QGQm$4gbTqGtG&X)-LrlYZs_Z3<EB{qL8izD;P7Q90%#OOtd!}fdToaCjhLPa*+}`gJ-O@P{Ql;_xy&FuGz!@TB3mMf4Wh&Yxx{yue*DYlAM023_#Neh91Fj+P~Gdm7pb61;sow0$)PR|P#%}@R2A=$;i2z~L!?7>-@E+%+<yVa&0g)$eWAlpN&E7>dj$H{D-`-|{0iX23PTW{1J}O_bEiz~#bd1sowlvKq(r+xy#Pd%b&^mx7ezXtM8#>Yj%{<y8)`K7Wvc#*MIP^SWZv2YwH&jNQYqI3(Fp(qK*BnS0O<sll`RwXDT1r<mK+9|4b#4u$4gtN>|6Fcs`gL^F+Q~CibU4{`&gi8u}$Z#1&JNOgt4YB!Ka(t2hFpR0x{sfz=lt_gT~Poq8f+^4|p#PK^nQtRm9v2VC5#%)OwAR&P%FTfLKC27`>ei1438*7;$45=T@ng8Hpo7D#ci7Mmvi<5i_oeB6v68K{e4=w2~A3=7o;zi_UBuN12URw%CW8=QO}Cv^&W;8bVxxAzOJ#>+mrYCGSK3@m<=`aEPgp@0Mmry+-=Z7{hR}+#(mMQx7Cw(Ma!u@Ia&VUGPoE;#``MkM9Df=?JAi;Z*aXV^wlxby694t4m#g?lc*e%3V}k$W}MP#SfR^ic9m>W32~Qykcdc1{|m8-1B@#N|24-n08WZtbdbbB!nwOj%Q*W4qOPQS6Jj_VfKX%{Nnn$Ph2Pi`dwa)_m&Y;Ucygz2||D;t)jB5D&*VRKKiF!Q<YhKAb!tou`CsR3qlIQRKWR52OwIov(HX&ZE4t}Ee$G;=}h!z2R=8VlC)(W{lW@hCWf=k4f+MsD&l?TDwOIl-6(yi!4hRL$pp~`A>`y{c%w--{Q_tgL++{C+0}W}c`8b1UfWxD3QAMuYl|`mb}z!_0d@OYhQG%mefRdpbTnqL_@`2E!qaH@JrMu&&(bYHi0;@w5!y@oyaH*4B6gF+8M{tU9G8?qE$~Rex>tjZXOJ?IAmELK*%g0m9`-Wc4mxm!Gz1CYE_A(n9uD6zp36VYmiRdkfO&stm2!qt98+1Dqkj2w;i{wKv4?E9OtBj<MlXV0Oqx|`EyWdp)$ht`M<t}=b1NYsB|*0#{{=GR+Cl~_=B+wY)eS><xfXdgT9OkLjtOs+3#85glJyaX<WoCY(eixd+~~8TvhoffzH%Z{NMjl3wfG+9aUVe6OcNA^(E{+c%Df2Y^eN92WyqV@e%}Mr%xNKs-R0y64d#jga}{s1Wl%5!3>&9r3HWUcc$pY@#EPEA#&9b%b76;P&q#|>0+f>Xl<;5)oWdXpy2`bDtM^+w{EfTK;#<)Ppl|1#tdTqsj6&=@3+FIw62VE`5q&{6Fk?FW_|KA%m^6f_995dKs2lq~H9!)F#tcM)9C23&s}?|Zc=KLPqH1~|KGvtSq*HNgP`WS;$^OAyI&mD$$=;!A*61L`DpSEV;-@$<rBU^-2-t#E-dSU9$8MnsG5@s_T6JnU1wM<LN{0K;ONKp>9k+9NbJ^O|9Ioh@E;(C9l}cA(B?DpAC2Oj=Oy2{HALCgY@{bklG5*Qo0=&*G=2DSdUNb9!`;g81up-nbA#6c4`E|+{IapgAB8->HP-t*R&5n6SogiqlVctWvjNH<h`4ma;#hY-}y8)G5KKw~@1{IGvn>k@@IQ7f!MKfG>xTpEFU3D1>|Bh{dvqiad&7Sfhm~QoMpAaQ&VK8zr{H)O39*Q^l*sOlX4$Z{ih5Y&yWi)AMO1-n6+30CY^!r(cf{**;U;Yqn#Ei7V&%zLV#A4lia1$|?O(`NbbC|rp3jwh(BZ225RwX)ttTo!0d7%$cE9XuFin(DN(6I0@WIstd_`5~LQte`Kpo?Jb9E3r1S<{eHrm%!J$Ke~@^%j}dF4a?QA94FI3H>6m)&!cxm=&K{t6A&rW;PkQf-!n&$m{*l2=}$oDU_P<fXsfmFF|Wv#o6Go5o7ccs(HUXi7sRZM5VWO5hag03I(_ZtHQ{&Icn0Zjy5XkR%+RTsKv)a()!9ycoW%Fb=fbr42r(6$_8Z)DoN#6D6*#s3DD(w$5G36R$}t}fJ~gz7D1@n+f2<nf=I<!Bi0~p85O37vt$iHs`3XP^+44*8E#lvR&;UCW}e~WbAy*cyx+muXUI%qDvS89ba)<6ZAg7o4Sb3pm8T-oh)Q77PAQ7R%~KSlxh(_j$4-tS|AuiJO92?Uj|q&2B?6KRBMVfbh*|)JCZ2)DNU5p2d>;a4pr%M?fMN0~-ey~LPK@>C-CMP-Jfye9LGd0hP`@QAB&PTo7_0117gA)}z@!}6y`bxI5SL`%F_?sG*<u(nqKRk_UQmU;l}#)O-_)K=(G?WLY|oTs!ka2)W)^!C2IcwhjU0{<t|0punCQt*sTtxa=z={G({}^`Om#+S;KO354r`!Ot=cDsh@*9;7l&b%n^UlgyzZ{}iGv9>EuZO>@YX|Cv3L?GxOcx>3RPc}Mvy+xD_0=TLhW^mh)lU>s09sTeVG6cr=OzFx+hZlT&tfWZnUf;;=@!G$L&>nGS5Xr*|)zd#Tv1{F@fd+ETMym^CWgn#X&o1xZf?KkP^zc@2g9v)yin$C+G&!8{@u_b+HeZ*$;J;aUJX5ecUzmQnO#&i1w605llXj<0EdBbop*6;nZyVAgZL)!DxljMHjk9-$cS`>ljc_SuGkFe9q8LvZuoo((3K+Dxr1;UAS7Dw{dz>a@5CA-koDb6S7Rc;=DN?wh_^YmkcKjGhOYKw|8A<KV`uK^%%^|#YdHzP4rkOKRxwXpsCo9v)T|BjyU#G3FIA2TBD$|)FML;TBqZBLniiPShkzgMD=^V$q1E4OUA2iB&-U4X}L?$^gWH3zCsB_H`pUd?Nq9+?f37B&gi1^0y-f3=!!WTcHERP4e5+W<m~dLrX<Af*Gv*fVYd>a2hY~_zAc}YSx~W!O$NV@jT=XFxZ?!;{$h1#>r#$zMX*b)jGOjtNtV5rurb&uU??^>>V67Zol2k&o%C8dxmYwql$Y&c5*gM`rWo=suQUGX-w!5*`W~bxvDYUv&VF2-Ak33`l@@u7DWto*HAv1y#!qF4JS_An_pJ?X0yt)%0mkg((J2(>>~5YU7}fOBuYFL;3|de`Jo0LCdkm<<x`Wqmh$QIQ#EL{Gtuwy68JB@JJz!j*(qn;!TGR(#*gS<L+L$Qj9qCk#ut{#!CcU=5L9nIgvF%QxH@9EfLzpU5p4~`gPvYFe&d4&KX_kt))NMCtGO+yA3UzMC{ERJG^!*2M@Q~;sxMK7GT)~Tv&ke*R>gqlj)hV}NzSGI;0d{JA6d7d12koju^EUJlYZm1y7q#UL`Pg6z1eH|{Q=uaP8daz}V$GQIORG*)Y`=K-$eySw3Z^ew5R*`&cLK|_*0Dv0;ietN%_n!q=Or4C1*nNL)N>%bPd?)CEus>xpZfTZBlx(?MGz;nmlz*N+4$t;NLh`HvE9!PWcXA^YCegDTNnN6Ngs<Zt7(;Vh^})I?V{KBcI|R4+joS=MGy~lgDo6(15ibnDvAd?gcv5#oKL*@wss|(NBdP~LO%eRXC-^98)wjUk2;)a`J<e{El5KZ{X$=-g?V!d<_Mobu|i9s^1#OuV#4H)K5$?!9#Kn$j{q_TvCT?qSQ(GFToP=3*><*`l!-f*GK23Mw$2k#ARvn;i?!C5q45TG$H!qnevr0je>(^!zqXnbII*50RC-MdjnghZ8dI06L?DFgDW;~jX>{W{$gtd4t8_qhzE}V6F|dvdRX<v|;Bp-x3qz&#v8@u)_5*W<QxjZW9f_SAB_M&5FN$W^WBq82a@rfR6Q_qnP@KU-=l{A&INXVPf0mpm(Nuq^a!khCA=9H6@mrLnhqP_Q_%hQsy!+?_H$?Bx-N6BFoXfImrZQF7f;$BMY;v6nk5Hs3E`HGL7f$|QShg)Md{iZG^K&>k7P+tm(?N^P?}P;pNOU!ubPZ@l-q61rl7zV^#HtdJYT=i5B?RuwZ9VGUBtl?;r+^9HqeWGv3GCOhdIp9XofEAA0iGx%N(#k^YZb6h`g`D-{$#c>l&1^SqNR3O=Gww%%EUZcPkCV1>{HZcz%3*_$xdGcJa({@#l?)(VnD@W9yvv;s+V_QocK-78_11|?VH((FsmD};@UtDYObWjh$TtY^fza1zb88*INYIV7^aMC(dG5Fcel{G_C_pD6KSijzX|{s+KiNKo9A0KD@9g&(ezT5CXASe&CRq2hN!Yf+jTJ$<!Ek0a-5XFXex4^i_EtYE}r7eh;XFr{d_ZlV`T%>mU4&T{beTLJ2Sf91rKtu#Z~gc&_hWwCUP#WvKS9buYzEIB8CKXMhjIkZA74!6Ob`Lp2kU@r9o|RGDwYT?MQ5=>DCq9P=A=^K(?&P<NP`~zkE@5#@hw(`hhC*Q3Zf5n5d=c19w9VePT@O(d2c?Lr553#75DhB`Tg0H&uH&Z%gkuY9|@eUmM6w)Zp#)S=Zw2A$>c>C1FyTC%?cbCL_!G7J*dyA|+&jd0_I)#l@Iw%zl5|f{-gdxV<;jmTdr*_gw`BD##5Y8kM@-)_W|)$;{*-sEQi8XahS_OQ=s%fw<`MTs_s_zB9(jBh>mbQf}b@;ZX3xjx{u+AYD?al<~_5w-v{El^xoqqEB82t;nLtb7YgbHsnygtL`VuIUodGIq5RE>(G?sU6UV5N%T{xr?&IO-y)3S&ZNuhv*9uL$N15Bv%Gdu?pkyMFt%7d+edUAN@|#S#A%COw6ffY>7#+0c*{q8cXLWqpEtsk!8LnsUXH{D?Z?ADnImdE^~&LKgXNqlhoP`L0@a{!DV#)7Zuh%28?Loa4ThsF$<i&#lqwm~V?EtNZ-AM^OqSDvgKAk}!{iUK!S93_=-=mHr#)4n(o{<x)im1g=URvt6E_br1&Q$)!Tv7hO-w9Q*}}K(lJ!G??h@cL<Qzivz6rRDCVtw)59A6s$9fvMvK+KaRy!dh8cEM$#6V!uwi?yxX+4<}&4y!E0(usx^a!mmTz=wJXf;dO03na0c5p`9B%>4)p4{%fJZVVXAdTv&+E&6J-rRT>Nt2fnui++_+=s)9pZ0n5Q)pGFX>LN`=S!_rUdX&>X`hqXGtR0wsrNj06fPW!DlHi0nJGKT3!pYk<4h#>5KL^uex)KgvOVOTo}7msW@O*4nJk!>nWJsQeP7`xwtw)L{t~bkls8SYId_iIOIO3DR7`30$uyb`uJ3{Ssui*nA}9z1NT&eqmiuR)3ME#eW3IiZPKxmks&$7d)p+O%!W8~~S!pW%KKG6Hs7&H8Vm0S7&3a$vR0{nIvkmTk?!l;BBcvutm#tW&zGPD&dgN1;X1m{wgZ5#Xh#S1M2{QQeh3&nZ{SQo?fAJw_^V5c)wGT+?!1-V9=4Hf(XYLd<3Byn7x347ND)OsqvoC*aIm`JjAqYk3?K|6<w0Fj`MJFnAqNXdQiAH_?oEw*JL(!a=w_)ytnh*(}z=0)GE@pVY15gR^n;{yt!7Ej!Url{Qo}9h|B7sj<0lSJiIRQP<3B$9FwdR~o;PE*SZ*>B7W8(&x?6S^rL800rA1{Ay@zDSSAk}0sPFqt9z!Z^73y*)g+=G@a0oO7`p+$4g)ZD05RQ1>aa2#$g*g^t04f&PFhR7}DHC`O0hk)3)zxd7BiH$P9hb;SXw>A}TJ1^gXX7^(b<9KWXnw-8Jp_BctS`{hZx8m&0>J{|O%B1wa{QBchKm7gsFJFEx1$Z0ai0)i9NyU1}^kyv?Yl0p;C^o+rN)$thVBZ%OHb`uvaNH*8!Iv}QV?#j=ainF5Fh@>7EdKGibLAI1$c^u?1E6V}alG|yn<jmA;>iR$G?Ev*_=xGejG}%wvok_g28wd+Q&g=-{@j#S25R#7U(Mww=#XA~F1um;-vAV{S&D#5s1_s$n0P@pGzd%wy2y2!@{jR)-NS=EVLiUjE9eE6v2x#9afKX@7mxy*K!1M;6cwvYnJa3&m!;M;+c(8r>UBl}NgB);JQr=T(8LpqDGqeh%&s#UMPoG{CRAb<!{Upi!TultG#3SHb8)Z#G<gs3cFuyF9X``N$U+&cu!!p9+x_w8fjY4+I)bSyswILQ_4t4coPY4U6#PM*J~PaxG0~$spc=!%+6Cs~$m^~=k8)T=OLB3;;JI8lZj*(qIkB<&#JKF`zFw4kt<**0c<6SSGN4o|OK21t*o@nxLw4?t@~V{f%T+E45B;WJO0a&6QkG`X^Gn&Ysft=M&KnG@s>%?0CK-kiGruf(Z>0;bmG1{a4<tS{m7{Kv31v#-0{9LSiahEh$w2LVn>{Pv<NY(v2EUAQy}r@Tt8iHuA<GcrHZ9|I8sq@qr^w9ZnvISSGQ3yhji3QXXO8pzJ0=uZ{04{m4XS#Bc*C>wYGTKdkEgPU(fn7L$2e37)bJEHru%4&w<zWNnwUmRiiXuc5oh8W*7yU!-_rfm$KP)@|MkCU<W4`pQJ~q6DOEzGoD3dC!C0An^Fupe|Lto&|K-O&fBxMzznorc(^tR#>z|&Ue)ibU-YdhueN|nlz4|oej@~}_GL#JdOwW2L*na)U-+nD}kD-I$;$fR_DPQod{8GH1=IA;9X_C?R)8>%1pfBFedkReZ^V3gX{vu3dJ6}A4H+<U5w<W*XtWGtgyOdQZnv!@LGN(NC2_r<xK6)NttJW)udRHndety@en>bu_p-=2gZ2V9`6#y%I^+o3Vb3uH@J+E@?k=xpYk*^5f6X$#J*w<-3Hl~@@J8zYK{q(+^|JJ+@Df>l9;|3FN_~kI)^+wx`u^VM{cbiaHP*XIbF`?)0b|zF@NlO!Yb1}Obrj+_ZUWaP~r-;0b^$io-KE<yFH+CxH-ol$?{b?&rTt#%~JG{b=&v{XP_Y5>R!iW;Hz~$IUL)F?^G33g;Kww*eH{}q28(_K{H3k=rmh{GRI?UnL*W6~9c_;U5yrn$S(rCBMEVD5-(s#=vCgOv^?Xt8sJKuC=x%EHfP`bDM6>EWaxObr;@xH};%7kZz0&VQ)NSwuzrwg7pDJ|mnm39FWd>RO-()5nn0`1wHRFH+6xHekLTu%#(0&DpudopuyP0vjv+^H=fcGox*1OUJfzO3oqL(0!y2a;l&G!HDAw{Utl%r%)aRjO@mzETw)?zD1g-k1228aD~7d^5o_IE7pfzc4TR8tViTkl}atN+H}NBhhe8jysTTHHswGPc!Q1z9?1Ew+q?-?z6f?cso4@0aj&??~uW}hBFO2j82Zm*Y0-=!yr?EO|rD(^KzHQ9{Qq0(hs_!so40ifX5I-!}HC(5wqFqc7BO$5^+qX;WDy;)|a67-O$L_bcBxnqv+s}9?>!Lh}Ip;9JSti|H2<nJ&!(g2sTE1obN%97ZxQ#1MH&wetT_1mr_#XTD<m!*JeCu;>KlIm9|^=Fn8-3m7Kj&OO86m!2VaftdVm?;<cwzLHW?(Ti+*5LVEYhSrP-aJcL@M1b8hM1c|ujSr@zB$eIfkENk7L?Fz2<d<gC*Nf8EhB?e-TTrFddU`*r!z)Hl6eAw51u2xbNS<#f76EyC@k`09t8}k)biM~df$Em&2_qhY_C*d1!0a?n_dz`!kJSW5RHzR<Dc{YplplfCF>ErL7cX!4H@^Z?*Xx9vx<bIY{GX$uRj&jGmTJ4_=QByW;SmP-kJCLWGG+BXLxP-I-n+CYnN$9F?H&aW*D&-Pir4HN`%VQT-6*#spz72luX_VsOMqv*VfbK~q&Ad_*cmSu-I!Pa5oh9CY<i<%%#<<!9FK}WPonmcs5W-z8hcif~jKqxw&v98A2477?M~yKn#UEXdmX707O>}$xHNJ-x-N&V+*aetvas0e`GT)`W-#gRqI%>z&TCIp3oo|;6`uzd3qJBzBL8f!rVds%UD%0fr5Ps1<gAh@c4&sH&1S8lXZ5oOGr2kWE`8cCA6f@rYXusYSKYU|1)y4^aUrUmhz@%Ue{eb@3z$IEMb8NpY=hg9B2CQ2gI(Mt)e}m_`swZE115<WQCVh<^0yBXDXv;0M$wUM6rk{4Cid(g5kX_QGM6%`{g3!0U81~joqLn`>d{Do~4o6EJ!nUjJ5Rm(45OV0ifftuQ(up)eS~uNIdM1q}#sd0cNd<O!kl8t(aC)IF;)6+MqBI=w9GbKOPIbA|M;CCamQEJr(k^>1%~AHat~22wLU<>brv}epyaT`vqFI(0nuSe04A%Bv&DlT}SJLeDU5_MJ3J0#AW=0m~<GuD`3_GXaP+pu(Y_a+&%EgsWwQ}+Cdt)Q?=C<A=OAimJx~4Hqh__0C*Rv}w!(sK>v=_U#9V*GnA4Jx)9ECSx1ki6=q7MQMP8Km*YS-5{REH+nz)UHLRhTkAJirjOZjA?8=iqo|K{ICqihYOU$B-Y{yeFML7k6@E)n)0%x)gR=+(N{#2olf4rcvEDx?d@ykVxOC(F7@2m8LoW6l#wnr#c)DZ>#BQeAZZ(S;0z(tWb8aa$3h38z?<t@S(=IhvO{1j;pYi@4U2921!(zCfH=BcjFwoVO%&0|8_>IJE78z9yzP~B?z&PGYZjbe{Lm2lhr8ErP)id|E9e%DF>3Iqr@(xv`(dC=kXU^>-#-cfl~Om)cNbS8N5oM9MWm4BC1r>tn!(NOY}Ttc{r6-#{hkRO4Tv_pGrE<un+1U3-s2T!r03W%w^JABPoR5Pp<slfS`RBm`!r=VN`+tslt>!c&s~^y&x7Ii)FU3sR_@=`G?k7WatmslVr8Fx|l<j<t#F%h@_O2Ol30nkb6jjMQslv4Kfw`LX{L(K8R|#c0|xDkNPo*P+MgkxPmtr2YPxk)a+GjkOI6EF;>PiT=xTzAkztSs2YdY)F5eNGq4%Nmqf_aM_a4hT2a>KiJ8$vd*aE&K${iVNI!HW>(G+^#d71s@FpEnX80N}JFD<mKAyhMpNqW1db2ooP1FcjU@9Rz&(t`2&FuL&KRu6$fCLD3FPTdftK7A#h#M?(8Yw-rX>Y1{zXhfxG!<Z7MT{>51!{cA=N#1KKyIUsnbGz40^z*x!MRE-R6a<nl=L>JY2}N{9dslX{m+ieZ25m8DZ>fc?Q#{`6+Dqp(M~0-D=@CD&|=rN)oeA8hG_%aF6~XYre<l&AD7o@7!NJ{6!pQ4+7T^_88VXejpia=(MyQ=h+RY;25qRq6Up6U(LOe3#lS#I%&O{LgL20L6Pd^%2wTIxh9$N#@uof+80KV8v!{5SCESaS(@~gLnYp<B932wzN_)hlPi5llgIh^#ly6JoHIn1D1s+qP*nULZz`wfOfoP2`q1+OeNWy;MO{ELieQ1o)w6monuBf2y6+7-lnPKrX_?%t~dOg-KX3^~=H%g$Lb_^6tI3vL#ma}g14C~^s;a+d5>!ZA+4Hc_$&Qy)>b>5}|-(py`JUdpi%Q%kwMLX*(wbwBiZKmko&;~C8bC1<<d0^sm5rHOVSVI=xhvX(MsQ@O17JpC$u>x3qIm*of@mn><uAZfaO7%QBP6^W4*0Ja{?xIBSzkd1h*C&D3&?q4>x|36$)KdXRG%u+4j==)cx4-KMB)|NPL@emn6o0AyK->)P^Wx?4>KVA3fWdMkad-!6j5)u3>GzBF*})zqXxU3w<o92;g7$)zgeGHj?$rDA(OM>Sgbb#Jf^DJ&9!do|ui$Yhw?itTQq}$<qiEPWprf(H+s(TTxAx>zgExQE@W5j2Zh(M$TN<@5A!UF5_-6d^e$MtpUWT7AObJT~sIBv$p%OO6P2|`(BHfb48XYka<QF|8zSYu3l3BJ0EUOkfZo>lO<CnRqd4xe2=~)xAByp<^tQNbt#jo<yq(CAx5AWz7eEU41tGaSLR8jFbD%6MJJ=hLh%*Lc%^n+W=-y^FOXoVbPn}yhaAZ|<fV&_8<I~GIDBX9hhqgk^)=A=YZbh9;y+gAo25w<0Ykg6O#n$iY-8@d{LEy@iyg<E1>t`%_D9y_~8gabSn?Qd@U377YDHxm@E5jRh1gF@DvYTF~07H8;j`(V|IF^dz5ueH%ncTRzQFP9HnX7)BOw1>?8vD1SP_ALYJ(EtftGu%6cOc+&68t0jfZjZGQ+B<_wv&}-hFJ`2wu|ufO<yo~uX8LttM@4z6x+#%eqXyCRS0!3g+zF`M2$5F9aoEwSKBpXVafAW|O9%;M6koNR=63Kf9R?Z3Ui68?B~!F9)!HsqTaiofIx;C)(8#k0*m{DPuY!bqaIJ~sU!)n7H{~P2VuENl1B%{hM4S0s^W1Vao%}rMSLJ3PH|2qf`lJI7<L+1swbK~v+Nf=v8<m85`~xsR8lONo4^G~!NmpOP?jOUR*bL@iH{eSk2SE5A4Gl~+GuLU1V*|R7m#HDYaO~19M91QMlob$1F}>n#w=0Nq{GoaslvW9;erdl~<2eqbC}00@O3GY%6C^aWkESJdC1C2}CYn=y8#E*HsnCIAQQAS&zcmT24)gYfDqI7UHw8xc3bTIQFr|1qw^S;fzJW#}D?=MEDasF|D=icOjdnHm_Vb9{HWjkHCB0hgqQk~b)P?udNgX>ZZ-L)w4c#j6G=!X3qolt{tuZ~GcM%U1(}@8|nq_Fu95qR)A;hTG3CwF=fUdFSJ@hmEKih&tb<_^vVk})x%)p40Y3F0XtI3TIl@i$^lVF{ti6Dygxb?*=e%KFAF%DqOrjNFOSPxxM4wDeXPS;Hu<*s|X;_mibxyDci>Kw>_<a>BagXD7VBC4RHZbF(cE`1%5As|28Bq$eGp=|LWZsDn$(~+|yPC5#nE?;J#P&9SK5mH^>c)1HVGfTpHV0Dg)h-v$`(|4rcLkxBmJq%u&gc^G_{AanLn^CZ;-u&dYGOq_h#9i30#`<g#Hkr2X+#}mY8fn|Hz{Jld9F*E~V8RWq?b6?`PF2-T+V8V(%$z6oHsUR$fMJrp5RjfHDojW4_kP%WFgUdbyaZ!xceuIbNfIO2I)J0EJt1mX@F_B}tEJiy6S{nMMitGPQ8b;*7H_g)_15LvxQ8~(EIi))eWSK}`~zycGUipiB(jpJYONe<KoRZYJG$f)I&65Nmg5swY8pgb5Xg(-C&`mB=%&NEe{6uwWT{!;GG!HE`+9b#y<f~tPB&?LMVK?m_Z20caD%^obA9GF$WkaL)DsYjMt5EPen>2nC{>~rIH-gVAyL@KAwWGA3lxg_yn{yYR(psJ9vf|$F6`L|0xzQ>RP^qA`j3J}Fi>gWX#}Q5S;r5nmRST26lLGU0LxbG3bvAQ;H-m=J@ZrxY9$s7?Y34NiAjNInmU1za=Ny64jC#j8bf-MYnppoY==)^5~Oz$nI5y3r!iWSMh)9L2my|=gaAdR?a~M`!A};n3&9kty~2{+vwjk8=<BNDrdazyrpO22@MR|gXp};%H0h{%ZHDrVn4SvRNcOlrx$EHk{^r5C%pg283fToBTOx@Kio^rC#CMl|{LAMb>sR%d9p!`^3%|6`+v~s=sh~=-1nw%yp)L+k9+&Y{74MPZq3?@Bq(gGwyZrs!e*wnLUhU9*p~Fx^`|`be)cMvc6v}P<3gE;FLlB+=*S`vLr%dd{W339EwynIRM7u$~07R5^l2AAoMLM8F#c8&VZF9^UYBcv{s{V^b2JdrZ-r5AU5VMg|Dc1$j2>=8@wmOLb=>(RQEfeV}f~)bC90r*U)4rI;OIxVyTlPGv_D}~gKD6hGKGy*ISfFUJP3Nrzi5<a&v6?Qyr<>dd&9jmMG2p+zhEKSI#?cm{8i)@MNG}a38oA6>#M}#D<tEewdySLMOR89aSVBA)y`2sNLRa?~abp<gR;ia6l_Nna#aL-ZJBvJ#F|LXtcsJldHBnZyk`w*rg^u8h&TJe<nT=Pf*oT|vG{7&kJIOg3LR^9&Sb0h7@G%r6??eCbUE0uah^dh8mS#x3M*7Ye!*H?OA{VMt4<uXBNbiH>K%?|skWI(pT$+)O?*gak2&F&aRP&)@RdQu@QW<!wOI?8OG#Qr4T~u7iRyV@M50~MJOY_#_s|Q!SVr8KQ9H;2q^L$4dkd5A$c2aDte3NA)geydjXJQ==TnMLESmb44_C;y*;`+KzTqpzjU0#j%mJw54!cTVzLVzc&pR%kc<lEXl%BNjZm05hCf6s2QEERnVLJGoE!1+rDAX>1q&rWb{Y1pGJ3M!82Ozvj~J~yJ0v;`jh!U|v}hO^BL`UTS};(h1(lj<<t$b6{55@j(71knZ|<m6^}qe(aY0%#XQ?y1_@)p^u;DoUtb+go=EN>k-)i!ujxFT&;lb^BU|zsDkd_x8qgG-j~)r&4ypQ)>7<5dZYg(k(%V?$|#O+DrPp0%?XKc9X;zyG~FXmoz~w@JPYBSA&gbkTMb>;EjdZ6@P3V_A=fMI&g(F1WDg6biI2X4&O1J%RkMQ_&E@Od4Fh?a)whJQ(2j#e))6Zs-xqvhhVr&u^TW(FM?f6npJ5n#T9_n@5*XNC8XnXD<L7pK(`_P1v2B>LIy16tvXZH4MTXj7I`*Wk`on<32&4Oq|N~n_7R8VQ#)DF@_gmo=(D4;@(v)raw1bmV;ShR_#WnQA3)zs6BLEf0`RuVya?y?DbEyT$eY-H-viUkX(5T-<>bf>=86Gx{cf{mP%r}w8>eOo_-zb$nHYG)ik`;Ca4R%(VTWhWNQ+Vel#=(9@L&m?!XOE{%C&r}_gg#sjl0d_ThR%iZ|9t>kvtKMLhL*X=P+y%!Aac_eL*%bV><l!&ytXsG=!)eRhqJ>8~Z;sKoW<>3`Bw)aaRbd7C?4*^IlG(YI-0()~B?jQ*mohx-bpN{=r;2aU9Lb-l1yN=pe-^Q^7Ujr#LaCQT49~*n(BwSz~R-ZlMV=|FsiZb!s^UK8u@5hWpS<hCPuTw{v-O*$UMhuIQOAIa@}RN>^be17X!AYpS_S-vf*v<5?T>j}`1O{>kD3yv{A=QjuI<Gb@4nkj?wBBGf1$Y(X{ob;=hxSX&(;jF-w#XmCf(j(J9%AZW8;-b1yF+|rr(6iM*Kn{d{<0hL`o{7G{L6^}WaIbm!#^~>%>GhBAKr}?y9br}l(j%|RmMY(j%p7J4>ZuM@T5G8G4Fmf^ctkB&aiZ}V#tbWH1&BWk^{Q4ASG-+r`y|bU$=xIyz`&ov9kNf0b{t#`%jI_hg!VrAKV%>aj6ET-fDIzy>n7qFW0kJS6f#)MuB|3quHQJbYp$}0j=S~BPxnUg8u<$TsKS?_HyG6xP?P77Di(u^>gh6y!(~wi9u!J|q;Tzrc7Ma#A)l+RBar-a{{UWi}1e(Q|6`xtFS?lg*HW|5sF?wmp>;2IP_qEX}l$!8>%zn8qL2F&b+2FAeWAqZLdA~i0E@THprMGqwC677^1-J&Q!pOBbYSOHZHY({>YT1IQ#m7U^`pQmt6WLUC*)O&XioUSQ24xN^N#$24vZo0N(B*o^QOkB#V)FceOq|meL8#l?OwBujNX1wq)*x;f6{d%?WDP;8@&_OFK-D=JZdh4XbaBsSp5fzjgO@_Q-@(~u$V_4?i}<f}cpgw~NPScde2O2Hry|mbN?_AYDT>3*Qxv4REd%YxPL3k~hH)E90T{WD35<s&0+I|P3sj<rS^$M6o`J?lsj0hs9|C5erbuUiVe%^8W?OVljP>Q+TeYn`q_@RE@g6Twza=UpruZ2ctL#u0Qe@h|q#W73pzCrFmt@~Dn1pQEVi+=_iD(dBP=&sgO)LrD)SgVy6%@p5&y;1tn<{2z7JC#1<@xW89F7sLAp01Y=*ds18R9AEf;|$`cLV`Ubw+96!(yloYoJrD+9!sHqjjbihhdhRQ?QD>?ymTWg9$Y)pXrqF)<agYcoHeNcfVT-RbP}wkUr2WS0K+q?RAQXOu1*M1r1_-nE(%`pQ6vYCsO)ctDhrow5%iI!&DW=?Nxg+&qYJox4$dJ8nM4If#w1%p@WI@Bz8^3K|5)<-z}q%63V#mt4pWV%4p#y=mydo<Gzt~u@9Ho4|SAr9qZqH+%@%5vtQhZ_LM;pOg@q0BW{&+`EDuU)NK18s-)DxXob>67rIB^M8aw77*J4IEgBho&d^S>r^6J|>h13;p>_scxLTaIae7j6)W=ZXonu84vP{0>yg44W5z&a33?~gUUG0^(cU@;cWx)gW7|hJYN0pjQ^jIiAJ@r|jso0RS+7K6xIQCKr<Q+^}qoA|YB0~;Zr{j7<CiY`kwwu&M^?Sa_2$e@m#;a~5tO|Z<xl7UXJ&l;YLJ37T*ds~pRI0A+_wS0%=%VuiIw1S#ia8s0+>|j5>5NC@?DD0iB*gC5OcF?8w-TcV&(`+7EuWTIP_d0o2EUJu8%K1w;{^QvVs&WiQjTy%uuH9soAzx<mc5s-G1w?zC^k3hehONhN}vy&^jbQ(STsYFm+fH^8P-mw81gT#Gydt{4<?2B9;7I-*C#X1eq5a(%#(VR7I};*q`SK{NX|vZPi2TaEc7Y&tqpDhIA)*$#_Z$KDHP`HZk{9<)%4P@eNf5_T2Mqh@@jH>45-7pgV%3}B<R`1ibN-^GrqeSmw`4tU|gWmV}XWR)CXSJJcT9Nm?-8Q=~RxeNp969y|%wWu%+j*?M|XMw_n;rm?~7B-AH9m;@rc|$TFX4mWsL5Z8vB#u>8~tb#BP~j4fI8{ReUIkmw<}V)Ou9!HbX24a6ks>OL9ODYsz0)5+@rc4~bT8Dzu<?W#lbHuMl{7Ue1zwdD=@*kB3-l~oN>p(6nrRj4~+&6x8`t4>sGzj*h^o~SAcrY~9$lTf2~0?V}4u|<dBrX9x3CwIr^B^r+fsEISwb0EA=KH~5#q7ts3`uL9{__)kP5GS;k7#~R4_~hkCS&fXb-OmqX_*6$~K8b}}7yar<AB!)mX_a({u5%LYqSyC!?Q$*KcZA195D#^OEgW_OP(_$3iU&J{7$(u2PrUiIb|srf`&DK_KLD9$C3~wIXV7(zI-F?vqnyDlNJAC<LSLtad2<Tp2%kZ*LQA3Yz{e6|!sL%Wa9}SUQA>r705S%#%}Q!m8IQPJ5^R0hcDA0Bi941ugYO%*&J$4}Ad4r9wbqxR@dkFs$6-KzkhW)kI|wGfwwe?;v7RDSdQA(B(=I+5Q<tkmAcX5Frlz)ObmKb6u-sUybU<~!SO4!Zu#OB>KU%opavdNGL#6extrF7q19OH`6I@*#iJcoIAc2!Fie}hj{b-GH+8eSHr-wvPoWVoq|GG*z+=+UBmYgWjRDY;)Ovc+G)1w&iTa=`Sv~9)sGSfG_`{)BVMDNet!2xcZ%d%>wGF8}uI|Tl0a-9l~P^2j?e$ea}PX1t6wk<DwR3&fob2vE`xv&M(L5t1rgar>sbTylF4QNH)(7zj!gt;ihsuGcE;g@zL1n$gjJ?h;gLSTWXfC=BDMOCE<?ANk-28J4)6RiOOo+u<r3dM<Q6|hhGd*GV>WVSJsrwi1grFL27+QMhb#5`J0d0^M<Q`Ba_EhIh3PG1B(cCeJi#f;TrK*eGnIYq0gmv>;C_)X3m$c>Bbo7svms~fT6+CUF#uB60>B}vuvH)n0XCp#lJ+@WX~ri^RR<@L6Ax6r!wMl4PfX{)cl3IG?{jFfGg=UX)^MOJ&!^iq~4jF^Yb&9n!GsIo`fbukm=Xl_GtoRq+5DsrBS%(oIQp5o1jaHQ=0d^3S#Wdqcfa);slWhUS|GrHde4|1`^Rr12nLrF3waxSj27!OOYf?$6lh6Hp*3so|0M4*-vkTF1>#z~%~L2Yp|NR4XkNNlI+))n1Qf0*S!wyetI{5m<md{KAC+Xe9YfhzM+1%NJ?sHN!xcS8()VodAN<aNqJNElzlM$w}sDxMNIReL&bOYb;pCmGUT8^}!5;O+HU*W&FVeLKb_VN#hVzrZLaBg^_0fmHe;C1inlVDikx#h7c%et+D8kSjj8y*JdBZ2*?{T?Gaz$PFSImAc&4do0Dt%;X`ciW<6T13Obos83UYxajg+J=Nd7Gsejy)cP_~Zs7poQ1HTzH8i6jT~eu(@yiIe6~}p%9onX%PhJPD$fC$|WRtlz<WRn=?kCGRAOu}G=`y(M(3Ip|lOIY+^i!#)w)4f`B8=kBq|58G;W7Bf_|bT?ymnFUT66<2wpcyeM|2%ZYM6P%X^UR8vfPO2qk)@v%SU{7b4pa7H^P*`HG6Jej>HD-$HP9EBWgVL%HeT?<(w&pp|Cpw)u3=GoJ3M?_q#P4uC-4MhNCUX(k;rADjCsZJ>5fZfSJThmeYcRYFS~!<PWjI?}QoX-{)YbJyoI7R7)P!G}`ayT8I}DHxDrdiSZf1{x0TCOe|E{!nf{{^+SN}65uoB976TJ3Al_Ve%izj<O(>)dK$U19JEVTJ0T+)NzY=$Kw#3g8rA7(J(&~DhGSL&dKRek2(2(&e&SVVHA~q5A&;bXa7NoCqZAXK-0r?SX-M55jq0h|R>B|N+;|sBla~^&;U<^dhr^4X_IdPEXjQ0bZbIPaORZF1$h>E1pOe`$&Z;=6_dItLE*y#~Eg0pQDLcsvpf*h7OeFRYOl-t{r6M`9J>;F9oQED}WZ$ltESQ&>qiw`}U*RXVfAE<860jGPH%+rScaG9aSHq@MOlkGWG@1>r?}7WO6|xi}C<p{drvUDj`)8jDC03$iuDz&Eit!Grb%!d|c<2hk6#jl$X)69c_l@_cOyV$NHRm$TdSB*L3jGVS4eoyK!Khp#q$Ww1tyrYKWK$t}<WrSqyWfq2_F<Zc8@#m%GWhd_?Y*4+4@{kZ@gZmP(}tk64@l|2`CsnlWyFVP?i4f$!%ynBuO#3q@~dmJFMn(~%lR%L2u11bJKLGGcgC_sCn|HIrYoh1Mt%OA8<%cF(VUpKVeW*Q5DA~afhAKeW_Z5?PzmvyAsV&8D^;dnO?^e4oW27hflpQeyNWtF0X@+P!?TXH=A2I8@i`E0bpmx`;|7@Qvd(cqq1qxJFMn?F(EtM=)nqYFTT=|c6p>2{kAJ${gO)7;*D^(+MRU*8+^AJl_1FP$9BwbzLIOAq`IX0p$SvhHUL2)|fY`Xd_|4ggjWWN7Ec<b{HWhC>FW-S?_hSy@cx(fjoW32Qll`t*6)E4h;_S`p74*%@r1Zc1`r}VO{QdhcUw$qHcpKn|?p!rV#d^u~W-S?Of*w35Hoq526hnz%-xn4(NNl5U+$QP4mowsHLqQF3q-BXPM@~U3{_(kU<rh21jqk7nplO?Ny!CCHCVh3{$pktyk{7)Ai0QnHqJB5CGeTAdigN8!RINw;+>}-ZYV!DB&E+TPkY0Q)yJ7s_02H!WihxU~79<FmctJKa2uugM$aR|XkMVll!-GCyJ-*K?=mnRta^G5Ug&dC;kOG@Pe}4%S6{}5|D{8%$rPegtH^p4)bw&b78q63x7j3c7#1o4t4s_Jat}_}%V>KQoRALvy;)|rg{vZJ~7X@o`aj*Y0c@OY*&VrmBKGQwOLK&>Ei0b6q{qg33I<YP~f~hO2C4wFG_<#(YfAG5${6U>QGt8$k(W5$`8pFcc1?J+&>#jVHa#%%6a&g1pxm-AIlZC7~v9bEZxa{S=UX*;T)J5WW=ysVhpj0bMXcQXQjN7C`cJ7Yys+9K2RW1q-{ia_^uzrkEmS)lOOWCujidr(x8w{+f$`E=c8HN!vzbtugr3<f>?*~E;BtA8jqi&H2WlG}$_zn|_JnAILK<#{+JuBbi{WH!6zl?IdzR}LBa9J23%Mju=E#q|><N)8N$js%MjgAm9yjSFnpaDl`j`RIHCKOow28a3$s(OQX!?W~iV#kt?r?QFB{8yRBI8+GK@Dw+u`)G`}DCPT_m_|&BhSfh2XW|;x_yfS-(*4xO-)}bm^}lH3PCvl0EXdO65&^M3xxsJW@%b-5{`vFohW6$3T4=ud^<V$=^z^gx3-Z>1-@d6j#IHZx!WmFV{r<Ht!_JP(mul?SmHXST@uZeZc2IN@pHg;<E&TD%Pd|P63t-7!{{QNwHe>uyv?_=<e=p|5Dc0}!QM}_vkFNLpAieNn?CO@(<9ZO|dN5}=TFa&;e>KCK<uD+-akNJ<+T*%CM47_(h0fcqobld^@!mgoGBmLjCQhwA9;Jx<^1C>H2cHt}yrdCd9A|X%SI)4-=DBMX!U;6k=ryy(Au62Yaer<vVk%B#ETZrQ!Xlys;1<8ySjBI}xW64AH4%z`akAvt!5(;$`YU~MyIU<r{In};x%V`85Vh7cXArcWhFmUBoKNP(ZxUU&o6ljHp$3m$Od&YulSm<%r@g*EWtiVxKCu4Utz$LqDIQRLW#HFlGF146d3vSAw}trs0V5W;jyqCXRgky%@MU=0n+KGV)q$9265wZ{(Q!tKeZ>k8#=0<``;10(+zn~vb-ckH8d;xau;nN3QczFp>)sPa5fHm_c8bj5%Gd3DvS%o$e~Q8Vb5GsAuEBq#!A-n~eZMV|h;U*v9ENW8@;U>0Y%m)RWNIO3_WYHQW_g~IT}~V%#_6VH<1LrVBL1Axkd9(GpN?sQIsl2!*>J&TQy!k7(WZs?mDzkM0a-oZP@m<moKS%R$RrMTr6^msRaIM`h%$N&IUTbVUh{^<h<H_5dTsNas&JKeqrMa+Tv}s)`LUgJLg0Wfp>*<$B?&V?9RW39JlcINv-gL&9>;x1)}pU*zmzcX&u_<tvF?T1`DnQ}jT^{zYPx!Bvkf%!OT242X9gIyo2kJTiX-DIg(!qVi^TA9DG-6qeNG223BjgSir%WDJXXsu4a;sL#*IU|Saog|94xveodT1$`qg;{W7BClmfT=j^IYk>98KS)Ob|z%fZTL?uU~qb%GQCB7(ri<V3&^Wb@ruMWQah#09f)LP?E0)XrPr!A9z}m?=?$kSD2p78#P?8hb0$GWqCe$YEJ+7?9VNnB8$<;+ix@Ss<gO#CBW1n(YNslZI9I<*V^OO%xNE5sUk~(W|)4%Zl+n)lhrefjES2&iVg@D-ImFFwszw{g*q0W>zgbmm@Hx9di1u>5lC7SEffjwaZV`+q*EVkpY>8c!Y;S9_kDXU)!J(aZ~%PY!u-R7vWAMLEB`Q0D{=0z#Cu;}jmPJIXvXVd&tjWVWApP~=={~2Qz;Yd>(D9X*A9iinNHsKlk9VMF*zo1@TMMe?>SwUr190w1>4c@Q*NarVo{4Fm~!gN@YR~ewZTJG<qZNe`o#`_Uwg{35;*1TG>U!-O4mV3vgFgtX)V@^PPwX1@4JNqtNYa_3?G8dIWdf04HY_m64i2Pi~}l(1?8#MW~RjI8m}p)-5QK=&?FWdD)pqNnub_9X5t(;G~BP~cQ)SnMgZ@dN<~HgE*FnmJ8B8!E!JI%V_$!)>D;<ww`8%7#rRJ--(0!h#kPzMcJYzrXS(beqE9Y7RDqA}r`qn2_;RKl#=o&exPEK=sxk6Ru?k3wnjHM98_flb(@FUHe_wCBAF2lM^EWr?KP;A{cVo>y;{?0`*Al-~3??SB9BIudTtDs3kr}mZL8{`<NauPNUp0<PG^vTHuBBn><j}UqMH*Oago(cqmEsI9*E%9{<GaEcT-DHI!@2Cc$?+e1cHYETJ;>>7yyCdSs?MRj$^P=Icc~p$-Zyk_VRxsU;yg@pV-6)%$3VOK#2Eh+SRlXjbIO&Th%~^{lN~AKh}gfTpKH=ux;eK{_!=fm>TfVsDozziIT!T(twnk=SkY=2jw_b^vS&XT?T86X$eDKJRc|j<%1LBvA?vj%sJSPJxnY~~mH&I#Gq9x`K?lrh2;5Y8ZI6rTu0gqUaU@&6N;|iUkFUU$1z$|wmc4%^=l#5oT8C+Re~*&E`6&qlUyw31B?b0~tb_1}M-P}0%vBMxnYdXGLaV?jkF*d{>HFZ#ib*na2p~!RW?|UJ@j*m=`tJzBB2vgv!h2vyVpNuG1xg;Qbt6z&nV!n--(Yq~6(ynQtEvs1ax1M4(ce~X@&uEHb7A50##LGm*S^_B-b@*5K<^!sWexvz(o6?kwEliDB$d|<fgX|zZqA4|tn-4>S%aFDDPM{$9fQZlu&yhEv-GaO7MuGzH>H>YBHIaFghwzt;$axZT(iR4gQ^bR`|14Vd*FbnP=_JT35oI>m5?h@$j5{XngC?_aJ~LgzE-ySIfpQnA`flUsI~;ecQ!LIv5zSC=FIvj(oNmM%Z!8d_}oxGk7b$nnW$=|SgaYu_QJNrBi0AvPMcj6h>WjdMCQ(Ev76X!KOr(#biXL-X==&uYLc>5B#oX54W*eW4x)uh_@@(p?QE#LoRq3FqsM*wqEITsA;u{vGu-)wjL=nhvfWuvom!mF#NklT2=^{ah1!&?b92nwd@F6y6KdzI+nR^@K7o2tRq>pNuTeFTlI<8|Sq<h{?O7a=wp8s2L`mrdcVeS@vhqwkVarrYY0)o*x^*NJ+k~nu+Enxqs)7U-{2RPJB_UK<42M(zL%Q32T}|6KclFamH+ZA{v6iXsv|Zb(gWgEewFU&g>@Bm&OJ)U{ZD&`p<iCFT^4G7%`fXKs`ruXIfj%DY^yp4|uQYXuV*N8d?;M82aCy*kCkm5A)l&?qKr6P?4<_?At$vPw>O(**ST0uIx!}=hH9yX!1Y<f)xdad@=lHEALKd=V7XZVe$Zk_IEX3qZoj)pKh+nN~IwOWgg*_N2UW4^N5|I95or~OF1zvjkJRhEgQc=@M_g=YUc$91W)~Mff9#<0V(ypsGV#`a^P}PN^xHiy6VKfUf$4Qomau(o`hWjqfJ@#)%Yxj-JZx#aMPb0NrGoUbfqicxPs&D0<Wx3c7Cu~H(pBMym(D(&O0zbqEu$oVttI1dpF7z6!#HbDhj~n`<hv(J^Lo7+%8Lz=oZ^EQ)Jv=v>yeGl%U`$<Q)g(UNB?jI_TB)YqEo)~5*!b1qDL|LU5k$K88Vg~)yj33-VcqUeF{bYb2sHg<_a_AxQS-aNcqV-WE=9WNx#XO`yvVnqYAfxKv7o3iXP+hZl#)}<IlG{WC0O4uP~+y?F}t2MLUg3X#|Vk*Fc^|+Q81b?<86`nc@<lH6mzT*GZ&xN8}6RZ<cADqe*R_&u@mF9kmi?vpnjJ%3~#(~DtWxgkmgit4{j1x<($Q!)t=#3hs<r2q%>ar?$Ak|zg*tB?O3lbxEQf#1^I(~L(bOhIKcoWtykxnu!v@jbloM5)%Aq(ER6IG#Y?L9AmPdKpo+=-*GZfBQu^}0?&badOJKjo9S8)ls-vsu?V$$B$zsuUWXko5AUY+j*lkfZYe5J-cHZm_<I^adQKRCRK5yywF>l^QKnrsazVQYYz_mnk=PU{5Hv+9<4MMZ;n9C_@fzSzoRCEXn!e&ZCUe87kvmbIp5wdU1Z8CeY<P>#+x9OVW^FZd?NqSI<MD&gJHC`t<7(JR^qv#sxS#X$=0^^<TN(jGqIL<!pobq8`*~yK-A$449oY(wNTOhvKoXdrT3Z+`IlVI*hf&U_oVP2(y@Rt)E?}v-1DA})E*18A<05}wJbgL4!F&=jwsgXt3`5Dk%R9!ZIS0PVKZHCPrd^D1eeqA;hI`rRW{c=g?!>CAU30jC+(!l)l#OAQk*xqlI*&)1xX+WmaEW(J=RBC#xVjH9^K*QvA$&id_?vlVN?^fRlX(Pgm@?av3HBtB-sd^DdGz*A`5kzR9+o-bpECZ5XgdNp*;ZMC&zE^d`qplI2P`5V=60RIT)EaMfK2T4K3BMU*RceCRg6lB936$Nn#Fj`ZGu5lq8?>vLgxy-Rk`ICkYUD;dq+GN|Q~wDF|00CqR4QJ{l9jXiNVS(Tx)-KF*GPk+!Lv*;Ho8QrJ-Jzi7H=PEKH_AGj8gl`*mkHisqvk}PqVM2vD9sd%*Q_fB4ZIjJT!6x&}8BEWZfNmMG<OUw3<H#_4ooA{FK(*2i+ai7g^r&wmaY~7xKE_H#z6Ge{2JExRZH<Q18%(5z#qza5V7y(v+h$ZTHrp!J*I*LtL?~1~eJa0B!w*%CK;yDp-%-fT@yd@z}xQk5So-zd^)+n<9(jGmv4Nky%q7w~fyB$FbpN9D(}sL>{Og5bF&sqm$D?6YrwEQX>RVwii}(OIjWKzDyNX&1P8weVmNMw5qh7=9+fs<U6wmiA8}q&kiR&tBuqHvEszSG!@oWl5o^}Vw;gD?;sGwxN;(<pcq5Lrt{+SfaN`ol=>-Rh*%fxcdNs%_DSrj7kjTu>fimrf#6~<fl*)Y4l`yCEeIyWgY{ux%6N$@7kNukJodg)r{Xw5+85L7AJ)fJ3cYmTT;%E6y^>cKO9Wr;;tl)ZDZ{Th;2<kF%=G)bMvyGmxHhwGe%f28hG?hB4IQg#WKE`)=3lBF{(b07b+e8D6tvi^J3(rP5Cpt%g48q;7IhHoa^ZQ=YSk>2gNj@Hcq&yYZVGbj4QIQ>R7QnPY}$_Y*O;18XT(==kB7FOA#2QBv^QqjoN1sx^(hU&${@QeZ!w}KE6+JFEu=%CODmS&Zf|4AbfVBPIbz#r7=VCHITxi*U{|Ou&V@;wiH9bIqw$By{1xmvv+&ahe%}JEj2N)0K7P7+^-(yyGMANNxF0GJLBA7Q1>xTU$2u#+#b`RRy<^;f_~xQHdaV*r0KCN!lnqC8cb-x67ylV5TZp)CWCU8F26@@Bt!_)&zc%MU45*v-^4W~}5a_E(=Jb7PdZL;dd3RCMeM}-*0VWJBHk&%`qfv(;v8;;$!Q`J@qf!6g8GSPi(XipC6>hoA5Y)~`N^+HS7cUr1bzE(uh(+{d5d9KZWh2pLCg3#T#H#%@%&kGlK)Ses<7!94tCR%1u85YFnr(T+$6jI}<kp&GSfM^HW&)w5U5NB@x)sA54c#!2*iADVC8udG<oUB*OfMz;s|elGaPt4F?p&7JN^&6jLtaQEEm8YsIA+xoz2Qp#{~I%7JxpFC4icy<JH{)8B#ZZfssa*;%pu2sB-jgcHy;n1*`ULOFovRq4A-cQ=a3#tcpSISVX;+9Zd*IP5s@UJxkT#~A0`9Q9;;s9arf=e7Cqp;zd8WG_ePI56-{~jz3QCHYVf4KyZrdEnK6IMl^^p5kX7T!n7SkQLpL9kDFMxts#nm!9G;m1oBOrVnJ>2x=vwPrN>rEhkB|>+a(6ZnbXu!#eehmv*826|-`b&jLx*AUdwbu;?Vts&xP@W{j&A`N^@<oCQ&_IFig2%q<8~0`%^ySd>l;o^Z#kj+<c#(>m<VqHr~LJ=9|bwM64YR*1Ux@(Ag@-STdAElwmt3tLzU_|yy<?i)2wq#Ac$icNd@oKook-^w_XLYJefMf!^76Beo+S4<BcS{1F{~wJ&6u@I1bCcrxTd1Nh)ogUq@w^SbbhcW->$OS6fIjK(GQJ?I{L_8%<lGO0L4&Zwd=Ahf8E?mwKYm9<`JN6l9BRhF|E6(j#VB2OTUkzmY{eL~*U02zjsmX90Oz{Jq7(^XuL$jH(S&v`2Uotf#rY*W3q*dd!&^J$Zrl>G<2BlIKQFDJxT86*K^p1X##}`*vHq)yzAGpnus7G<j$|D|JKZ-D43Xr(MzD_|o?yqUrDk$`5+)+moQnxF%|Ks;r-noaSAg<p<}_Tuw6u>!DUfd*P&jrV~s}vaA=z)(PTrtkHm*FK%liUur-Lg+ta~O~ujNi!)C=m7r;$U5&0^8##k>{oEC~&=?0c@++w1+DTIJc`F~};2*iQ#1%P~!T6TXH2iI+94Nd8BLXrY;s8K65E^Y%V91H+fWa2b`;mN`o}}{0%i>TpJuB0g3;{PW_rxpgYV3=&3akMm4F6drnSf5VKQPfWGV92esyDbt^<i1WqZ+&>gCS&DG(iii8o^+!#2EOx-4i!f07%gD##gQR2`X<lmp6L6W-bB4VI4ghl%F&p-3};blRrB%YbXSYLthtzUdGDKTRQW5yZ=N9{o|>5WFs(+<dniUEhi|OMD;(9dYIh*7=g-kGnqD7kl24CggoTH#5X{FZ+gXJlSqrpQVgJw5jB*r{b2{{67upxaK^6`i3LJPOF`R(ylG#(FfXs+Gsmk2reKQ?p)j!C=rYl9ooy>DXeXOI+1Ew7Zab*eljRCkBPlNGfRWbQ2ygR^)8o38&$}b?#@*w$jq22cF64;8796;tl-!5GK=7^A<XV~4(N(9Pv6)&TQvnZZ6|3b>yogN6bPutbLeb>*+2{?T3h<6FMHeMP69q2yT3Qg!!aO!;c4jyVIIJMo`3+^*n6EhylrexJQnW<s8L;D-k^#aM`P@tI0;>+Rh}!skd&TRb*lZ{ZZ&87#ip@Z&xUS5372SV$gU}~-P8`bAbX{R@Xs#p)`8@by82lBrqex{+Lp=}kIg~0hikcWo`^RosO{P-{E(T%{pX8^CsPXxWAn0#1Y<=azuM{ZE3ihZjqZ%8R5|=0hwI%A>K`suOlu_an9$(|s@d)$w`|Zu0<}g8vbQ;$`R>63t!bFZ(@9Ix&#T6DP8^FTE?7kwQ2%3!C|8_|gP^T#yk*`>?Gf{k&w-QO{)QU~o=Ecl%E$^0el6qE$&`A=7vQ+^;>uwgZQ!k^K2(03oH|>KrSoAb}@?7dDSM*9L@s3w9;Qv(0Klh(dNFFvwFP+gpez**#NkI&I1W)dpy+<B12}?8q23lI-u7U6RnMYYW9f4Gy6Fr-#;pxI$7r(<<y*$?K{-_9;20inN<P_c(o$Q3vqeqyrI>MbPt;VWkDq8PyeYsO|c`~`0lda);!GZ3CMyGaSOVNST=l2{uoON+)ut-KR``y9@o*hiF@U+6G0mL&};BPFLEb1BOlmGz|*Bw#lBGD~W2oAk;)-N&gC)L^`WjLLx-7%t|;0e<;4c}Z!xqzZp2*=ad{uxV}Mfs6GA?|6&k5FA~Pt0^^4ITXEEPyh}I2qzM-{xS5<7*L9JtFp{Z(`_wje`_S8aig3yiy}`%B#TfT5N{)Q0d8qCquZSL2A4e_Eq#R7^O%mu|DpTLfB&c)HfQy?onBJYNiD#**U@(-M~<~9zbWZSrx5ncH%Eq6;?COKq|zuki1dgY_N~i*)$z%TO0$ZCgE%ZICjx9kkXkvobdvZU{_(Rx;h0^=QH_ge5h%qC&RPCua%DC#aB;E#TUmopC2L;qAMUOAHuG}#8R-qE_W1HgVbdd5<dL`lwzxqh>H;cp?O(vAR;h3BF6q$v8TnfqJN~|aIGA6ab#iYzD_+S<w%}Kq4O{Y2|2&sjy&CLdla)2ub`Ppp7{g4-J8E4DPj{d$&{gF3xtrt(%@8bQvzf)iTlj$IdiG1<jMGm$;Ri0(zac1QuB3WxJANFp?lo&cwJ!Od_B5Dsc(k-l<*D%1BX7ogHp4n0O!1^&weqUWAT@a2S9~`<F_TTv{u^@Il-pJCG70}=uy=H$l5e9AFK>5sttW`@#W;ZuaTa#OLb9dgH)5rFO%!)Dg)NEE>jFH;fTaFnG-GCZX@AVrVw;_BZs<wf#VY*5$Ql#A5yQT@Nd?%ELLwKZe(bE>Q%IgbWvAu=pCK*k*ShE>QaSt+<eX+jrzFlR}KAmM7hGuK8r^o_Q}*z)uJcl=hF6}bi_$!vp`dQqZ)x$?B#JMJ_~cX*15#v(_}?krvjpzY6vu{-O+4_0guKiIN#;FVW(oE<G?Q|GZ$xsrk=Df3Fzl;91oskPOM>(m@M}|m6G|GjYCzt)>GSgd#;0yQlOJk7@;cS@Yl!?yp~qPqb;5zcxR;Qlz%RiO%8i!R8io-PRYC-(0a6rVWw6Zt%0j-iq~*H;?*Ei{dvfzmWw&nwlgMvlfxd4dP>6Ic|7b$;CXa41!<Q>twsQG;5+^_KI?Rd($Ms+!~)*GJP;Q*Qsai&N%zVf#kG#`Oq-U&!g2Xc3<t4`k`8(GsYo%EtW5|c0bWn9tMLvgsYr)OEvBKEX|R(z>!86qb&hgNo^bbd;eG|l-L)S0T3sGGUC0!ei&iV#==zo}^F@`5dgcXdGS_XX7N-%~pu<>o<5;5!<t)y%yr%%Ayh)CFr+G=;1e~af&$=dOS1#A6vQ``v^&4VI4u#gU>Xd8qGS0<_R^^qD17WOIngh1eNm<<>DI*zsrq{}k*>^)hsU$*&eC3&s4t6BWsH*&_kaVIc7Eiu1Z9vrJxWT@NZQyvt=)^@YM4YfKo=?^E6?Vcz_D-ze!mDy<y-z(apen*EUJpx1Wvvkrc0Ha|?%OO`I|6U1u|0n5|5w}`VwmK5I4(DbF!;`VRYt$bA)C8R<-9*t=g`sA*<=SSCdB#~HfyKsWSm-LBk11ZzEAqNjnNMx6v0rat=>@;37D}jz~*_6tD3sSFsVGHH>GY1S!2C)s+2HMM*!U*ZGP)Bc?z9|$*4N%IH7?#m0;Z)J-qs~hpMsa^-~Ko^Pk+GKJnHSFDaL?-;!yJxcd`HKIPC9d#o|j(kgY;WGvaNibdh{SaG=2;EX-K`h_PAzNjRI1iW<(5kkN9l&90f)jBax%C_EyGM8-FU6bg{m0JU!PVz1f@9G>end^|L6GnM36+q?1ikf_x8v$Nfyl1kB+#>NO=}+WJ&w4l#jLtnBEtlnkGB9(x54tE;P?WQIGW!R0C6Lb$tM9mGx6&m$Qh&sS0BS_=MEq|S*W@iDJHIx#KgvishmUYHIsSUNS<Hz(;#u1mlJZS-|L>UTL(^;V9l#eAkeL3DU0@>xPsF0&@liWHz5I6O&-adsPm9Zge%AX)C&$f30O+W+Tiz*+>}T3NeY7X;K#qL^p7pcKZSFs<F0IE<GDK{gEBE}ECQ|ZvslWqh9h!y7)@V{74*fv(-XXd`^ol2~3CDV?4hKJH_D+eE-NSmMS0joRQ<iUeNqC4raqOp$gzvDey4#XKW}|*`G0_!eSA`TfAzxI%U}@8zn;965>=5yM<-|*3(0Q{{?dzQ5wGnESXrmtNY(M}D%L}0}#*@zE9F+mDT2Amt3btK^3U}1K%E*Q(LAITRtS~h<YFU$aXqIfU-Z2Pt@ao2R3bm=6(Ui~S@4$0GY=j5}gSr$BBCR|^bTgta6s)vTNEVKyUnQ?I<tPY(v9?Bw#`02UM-Kr4o=LP};{>`R=hxnp^+0~dz&EnL+EXiIA`XAEhr*Os7tV09bllaZ>IQ)MZ~Xl8_x~oL&XyeVQw^#xu3)O*pkSRnQ6=a(4;ek@We=Q2^K={?wAj3aktq}_DYceMnC9r%+l5voi4WS|I|DJ7L=Ueik&({v#T!l73Pep<lOxV@lv?G-FJR5LVO&2{+x(RX?`#T>ljRnFB^B6_QANr)@n;D#a<8s?c34vr3R2Sb5dlVvne?DVl_i}Z-ZQ25v!*NeH=t0>i3+RwofYXJmWm%wrOweEj+Kns41|>XSi;IG5Y4Vg`1^5u?i`KMW(kUM)Noe8*i-_~=Y8WLt|mepgJ^NNo(9hS==a*08T%HE(KpY`%blv_q7}9LTSM5P7S~~K;bUrr`!46ndJHhCjF6Ap@E-llQal8`qWEH;<L1)2rPmT28ilxV76i<h*5>SNH-y+%G)&M{N+AT|MoWyZMY_{uQqd-hU^zJi?+`HH;XzaOW^9a9s;msIHp8Rt1nUUjZ;rc+rgdihh29OJMDb1JFQ;`cU67~?%r&s2Hc=-k3g0CR&mq@5{$YwvZU23!hnUTQ^5=Cd$QXaPf|+umHZ7V7iPmz83zgYbs#DUX5X6m>jJ;?(H+84GLI|MW7xz`)2dYs@#Na45#AQz}_u`%LQksnOlKtV6O;lm+sikQsle?=qvmqMU-oiYF`!FakRDZ?{zU+!(dgDaQAmYmbsYpc;m&t6fiC|(Unn$|NH&;)0W-U}Vz`d*qV?Ljc>7?aUaU$)!;zLEAy?W03#<Dxs=?Zsbqe{CN$uf1O9PVS9Mo-9joN<6@FN{MWl(MXyUYNU~!xzZ7C4i<S+VVVx)QeAd=-jN4GsvC1a=ejYr3Q4>kkG*YoV5~hd*yyZCvFD|O!UD-d0zNj-gm~1<*@DhukEnv#F@ers}vKP>ht*vtk0$~ajES?*vABBi9Zv+*c}Bq=YpKS&5Ozx7e3Z>8tC7fdN&M@98O<3%9J>!Fy}=I(dWEA&vmOgy5woBv6O<yUK_(dD@Y7ydkuxY?Ljb3kHke%r#1tt6EmrwpR$W$W+v5zEtSF#ou;zBMu)}|USh%nih}1|r@;*!1wQRF_Z?Mac|f*2y<;bfQ^RkjAdSoNulOD2cnT#taTR&@(4qVLY&H2~j6ZvMy~Wr|OOn8p$t{vf;s3PHI2pd-ZgE_-%D2T{s~DvzVNX4?I*PqEY=)$KTg5ACHjSkpN4k71aMqK@A(=5m=A2z-eMIuAi^>;c=47Ja)!8;^WQA7QjHFTg?5l?13#hQ75#q`n5tWqM10cWNZ&BZJh8>&uUm+ofV?q8}bB3$P^;D^Sl}f$)8A1sJ%6)>wIPWNU$GvnJ8OiOLb}(wX7r6cY<=VgObVWW*Pg$a}`MqavOrvAWbj+rR9{N0y1blLaa3lk!^re=;?RX09Y0Y$XNtVvAZsS7N%xOC8(7+(hXVQ1~pZWOg{2DOlABuG<TGA<1qn<UInP3~^+GmrWjN&dvG#<XCIjkZy`G@m;VtZ;uwe37pH26Lu%yo3E9C@$(V0U&17_v{npy80)XN+tYA*hz9ynK`pU5!n6hZV<Zx|8?z&GI}eugs!zJ8<V!o<X<bc{X2HtU>Xrk)2XGaIN`UiBPtg3TitTF(PU6jZ->Bg()84sxFNGmYXM?sZ>AJkd5nZ$x<6>o&<dMUcG88sK7@*f~tGJ_V&e`2#wif2URNUy8h@23UkZ|K2{g8HztCF&C&dbGk6%b_>Uf0CnMF`OTKuajfIBQ|Ewx=um%|_jwH+E=$G%{Lzm?7X-@=#VS38ym}rsCq&%u`9$oF!JJQ9Sn8|xO@|2+m=gz(1ZhlDx*(V;ou0k8;bt8I}><Q+qg|VZl!27x-V15Owj;|yagDKneEu*W5L+NSWvB*s?j+0fhcwvo}q9bjUFJn*0Von_l7ACPB|D5L>*21gB^m9y(3Iz`RDps4JL^Q7)V+R#bIY|!K!CDrnAF8Ly)0(BgyN)lLezyIk`5n9E2mBs<_+S70{qMTl&K|&cwU}TXdWM|8;O)1o=2+`p%566D?zmW9+vjD7ocY(!@~eOQf}hY)q>lY7ja3x&__AM``H<3}e0*H+k(>GP+nn^{aUH+R;lh6uTw;7_KNA3!gqY+wHf_RTY5;(_*FK*wvy+PKvGX+)>3?x}dWYHULFg=nu-v-m*<KC4(JPV68tN3~ut>osF6yP0TrfQh%;HQ6+$1>5I-x)_hjCFXldIoULj|*eN-r;yqGU}F-?jD1i-M{C_9alM(Rc~zuU-}o5d{B>lTEd`2T@Ti4q~>;x$jX(TxV9N!jR)W-(nc_;pe~C2D!{CjjrXm-ab;bb#=yIbN3~ADl#f428p-3Y^CK#ETht7eV+&skLL3t#7A!`rG2g{mb~yW*$11YL3&NwqAq^_Lo<B){kP)h^VVKp{{!ny2?P')))
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
    # Learned from development opponents, using only their visible opening.
    rival = _farm(obs, 1-_seat(obs))
    return int(len(rival['hands']) <= 6 and rival['money'] <= 991.5)


def choose_branch(obs):
    # Turn 240: retain wool production when its market has held its value.
    # Otherwise use V3's milk-price rule for the four late animal placements.
    return (3 if obs['market']['prices']['MILK'] <= 191 else 1) if obs['market']['prices']['WOOL'] <= 188 else 0


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

_MIX_PARENT = agent
del agent

def agent(obs, configuration=None):
    action = _MIX_PARENT(obs, configuration)
    step = int(obs['step'])
    if step == 0:
        # Fund the opening without exposing next day's hiring cash to a round trip.
        action['market'] = [['BUY_PRODUCT', 'WHEAT', 13]]
    if step < 144 or _STATE[_seat(obs)]['route'] != 4:
        return action
    bags = obs['private']['inventories']
    units = [action['farmer']] + action['hands']
    products = ('MILK', 'WOOL', 'EGG')
    for i, op in enumerate(units):
        if i >= len(bags):
            break
        if op[0] == 'PLACE' and len(op) > 1 and op[1] in products and not bags[i].get(op[1], 0):
            other = next((p for p in products if bags[i].get(p, 0) > 0), None)
            if other:
                units[i] = ['PLACE', other, 10000]
    action['farmer'], action['hands'] = units[0], units[1:]
    if step < 718 and any(o[0] == 'SELL' and o[1] in products for o in action['market']):
        shed = _shed_projection(obs, action)
        for item in products:
            quantity = shed.get(item, 0)
            if quantity <= 0:
                continue
            order = next((o for o in action['market'] if o[:2] == ['SELL', item]), None)
            if order is not None:
                order[2] = quantity
            elif len(action['market']) < 10:
                action['market'].append(['SELL', item, quantity])
    return action
