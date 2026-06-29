# -*- coding: utf-8 -*-
from maya import cmds

# 選択オブジェクト取得
selection = cmds.ls(sl=True)

if not selection or len(selection) <= 1:
    cmds.error("Must select a source and one or more destination meshes.")

# 元メッシュのShape取得
shapes = cmds.listRelatives(selection[0], s=True, pa=True, type='mesh')

if not shapes:
    cmds.error("Source node has no mesh shape.")

# 元のSkinCluster取得
srcSkinCluster = cmds.listConnections(
    shapes[0] + ".inMesh",
    s=True,
    d=False,
    type="skinCluster"
)

if not srcSkinCluster:
    cmds.error("Source mesh has no skinCluster.")

srcSkinCluster = srcSkinCluster[0]

# 元スキンクラスター設定取得
skinningMethod = cmds.getAttr(srcSkinCluster + ".skm")
dropoffRate = cmds.getAttr(srcSkinCluster + ".dr")
maintainMaxInfluences = cmds.getAttr(srcSkinCluster + ".mmi")
maxInfluences = cmds.getAttr(srcSkinCluster + ".mi")
bindMethod = cmds.getAttr(srcSkinCluster + ".bm")
normalizeWeights = cmds.getAttr(srcSkinCluster + ".nw")

# インフルエンス取得
influences = cmds.skinCluster(srcSkinCluster, q=True, inf=True)

# コピー先へ処理
for dst in selection[1:]:

    shapes = cmds.listRelatives(dst, s=True, pa=True, type='mesh')

    if not shapes:
        continue

    dstSkinCluster = cmds.listConnections(
        shapes[0] + ".inMesh",
        s=True,
        d=False,
        type="skinCluster"
    )

    # SkinClusterが無ければ作成
    if not dstSkinCluster:

        dstSkinCluster = cmds.skinCluster(
            influences,
            dst,
            omi=maintainMaxInfluences,
            mi=maxInfluences,
            dr=dropoffRate,
            sm=skinningMethod,
            bm=bindMethod,
            nw=normalizeWeights,
            tsb=True
        )

    dstSkinCluster = dstSkinCluster[0]

    # ウェイトコピー
    cmds.copySkinWeights(
        ss=srcSkinCluster,
        ds=dstSkinCluster,
        surfaceAssociation="closestPoint",
        influenceAssociation=["name", "closestJoint", "oneToOne"],
        normalize=True,
        noMirror=True
    )

    print("Transfer skin weight: {} -> {}".format(selection[0], dst))