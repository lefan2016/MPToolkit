#========================================
# author: changlong.zang
#   mail: zclongpop@163.com
#   date: Thu, 20 Nov 2014 14:47:35
#========================================
import hashlib, pymel.core
import maya.cmds as mc
import maya.OpenMaya as OpenMaya
#--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
def findCoincidentGeometrys():
    #- 1. get all of the polygeometry
    geometrys = dict.fromkeys(mc.listRelatives(mc.ls(type='mesh'), p=True, path=True)).keys()

    #- 2. find geometry bounds
    minX, minY, minZ, maxX, maxY, maxZ = 0, 0, 0, 0, 0, 0
    for geo in geometrys:
        bbmn = mc.getAttr('%s.bbmn'%geo)[0]
        bbmx = mc.getAttr('%s.bbmx'%geo)[0]
        minX = min(minX, bbmn[0])
        minY = min(minY, bbmn[1])
        minZ = min(minZ, bbmn[2])
        maxX = max(maxX, bbmx[0])
        maxY = max(maxY, bbmx[1])
        maxZ = max(maxZ, bbmx[2])

    #- defind ray point out of the geometrys
    
    #   | - |<---------- . ---------->| - |
    xDis, yDis, zDis = abs(maxX - minX), abs(maxY - minY), abs(maxZ - minZ)
    minX = minX - xDis * 0.1
    minY = minY - yDis * 0.1
    minZ = minZ - xDis * 0.1
    maxX = maxX + xDis * 0.1
    maxY = maxY + yDis * 0.1
    maxZ = maxZ + zDis * 0.1
    
    #      *A     *B     *C
    #        \    |    /
    #      *D -   *   -  *E
    #        /    |    \
    #      *F     *G     *H
    pointA = minX,  minY, minZ
    pointB = minX,  minY, maxZ
    pointC = minX,  maxY, minZ
    pointD = minX,  maxY, maxZ
    pointE = maxX,  minY, minZ
    pointF = maxX,  minY, maxZ
    pointG = maxX,  maxY, minZ
    pointH = maxX,  maxY, maxZ
    pointI = minX, (maxY + minY) / 2.0, (maxZ + minZ) / 2.0
    pointJ = maxX, (maxY + minY) / 2.0, (maxZ + minZ) / 2.0
    pointK = (maxX + minX) / 2.0, minY, (maxZ + minZ) / 2.0
    pointL = (maxX + minX) / 2.0, maxY, (maxZ + minZ) / 2.0
    pointM = (maxX + minX) / 2.0, (maxY + minY) / 2.0, minZ
    pointN = (maxX + minX) / 2.0, (maxY + minY) / 2.0, maxZ

    #- 3. find point on mesh from ray point
    geometryData = dict()
    
    outPoint = OpenMaya.MPoint()
    utilA = OpenMaya.MScriptUtil()
    utilB = OpenMaya.MScriptUtil()
    face = utilA.asIntPtr()
    
    for geo in geometrys:
        mMesh = OpenMaya.MFnMesh(pymel.core.PyNode(geo).__apiobject__())
        
        md5 = hashlib.md5()
        for p in (pointA, pointB, pointC, pointD, pointE, pointF, pointG, pointH, pointI, pointJ, pointK, pointL, pointM, pointN):
            mMesh.getClosestPoint(OpenMaya.MPoint(*p), outPoint, OpenMaya.MSpace.kWorld, face)

            faceId = utilB.getInt(face)
            md5.update('%d'%faceId)
            
            posi = mc.xform('%s.f[%d]'%(geo, faceId), q=True, ws=True, t=True)
            for ps in posi:
                md5.update('%f'%ps)

        geometryData.setdefault(md5.hexdigest(), list()).append(geo)

    #- 4. find coincident geometrys
    Result = list()
    for k, v in geometryData.iteritems():
        if len(v) < 2:
            continue   
        Result.extend(v)

    #- 
    return Result