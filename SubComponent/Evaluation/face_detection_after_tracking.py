"""
Evaluate the face detection after tracking step (all faces and only speaking faces)

Usage:
  face_tracking.py <video_list> <face_tracking> <reference_head_position> <idx_path> <speaker_ref> <shotSegmentation>
  face_tracking.py -h | --help
"""

from docopt import docopt
from mediaeval_util.repere import IDXHack, read_ref_facetrack_position, align_facetrack_ref
import copy

if __name__ == '__main__':
    args = docopt(__doc__)

    nb_hyp = 0.0
    nb_ref = 0.0
    nb_correct=0.0

    nb_ref_speakingFace = 0.0
    nb_correct_speakingFace = 0.0

    for videoID in open(args['<video_list>']).read().splitlines():

        frames_to_process = []
        for line in open(args['<shotSegmentation>']).read().splitlines():
            v, shot, startTime, endTime, startFrame, endFrame = line.split(' ') 
            if v == videoID:
                for frameID in range(int(startFrame), int(endFrame)+1):
                    frames_to_process.append(frameID)
                
        ref_f_tmp = read_ref_facetrack_position(args['<reference_head_position>'], videoID, 0)
        ref_f = copy.deepcopy(ref_f_tmp)
        for frameID in ref_f_tmp:
            if frameID not in frames_to_process:
                del ref_f[frameID]

        ref_spk = []
        for line in open(args['<speaker_ref>']).read().splitlines():
            v, startTime, endTime, startFrame, endFrame, t, l, conf = line.split(' ')
            if v == videoID:
                ref_spk.append([float(startTime), float(endTime), l])

        frame2time = IDXHack(args['<idx_path>']+videoID+'.MPG.idx')

        facetracks = {}
        l_ft = []
        for line in open(args['<face_tracking>']+'/'+videoID+'.facetrack').read().splitlines():
            frameID, faceID, xmin, ymin, w, h = map(int, line.split(' ')) 
            facetracks.setdefault(frameID, {})
            facetracks[frameID][faceID] = xmin, ymin, xmin+w, ymin+h
            if frameID in ref_f:
                l_ft.append(faceID)

        facetrack_vs_ref = align_facetrack_ref(ref_f, facetracks)

        nb_hyp+=len(l_ft)
        for frameID in ref_f:
            nb_ref+=len(ref_f[frameID])

        for frameID in ref_f:

            timestamp =  frame2time(frameID, 0.0)
            for startTime, endTime, spkName in ref_spk:
                if timestamp >= startTime and timestamp <= endTime:
                    for headName in ref_f[frameID]:
                        if headName == spkName:
                            nb_ref_speakingFace+=1
                    if frameID in facetracks:
                        for faceID in facetracks[frameID]:
                            if faceID in facetrack_vs_ref and facetrack_vs_ref[faceID] == spkName:
                                nb_correct_speakingFace+=1

        nb_correct+=len(facetrack_vs_ref)

    print 'precision:', round(nb_correct/nb_hyp,3)*100, '%    ',
    print 'recall:',    round(nb_correct/nb_ref,3)*100, '%    ',
    print 'recall speaking face:',    round(nb_correct_speakingFace/nb_ref_speakingFace,3)*100, '%    '


