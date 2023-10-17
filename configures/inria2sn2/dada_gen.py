"""
training configures
"""
debug = False

solver_conf = {}
solver_conf['gpu_ids'] = '7' # set '-1' to disable gpu
solver_conf['solver_name'] = 'dada_gen'
solver_conf['solver_path'] = 'models.models.dada_gen_model'
solver_conf['net_path'] = 'models.models.dada_gen_model'
solver_conf['metric_names'] = ['miou']
solver_conf['checkpoints_dir'] = './checkpoints/inria2sn2/' + solver_conf['solver_name']
solver_conf['log_dir'] = './checkpoints/inria2sn2/' + solver_conf['solver_name'] + '/logs'
solver_conf['load_state'] = False
# solver_conf['solver_state_path'] = './checkpoints/inria2sn2/our_gen_v5.6/network_080000.pkl'
solver_conf['solver_state_path'] = ''
solver_conf['use_dist'] = False
solver_conf['max_iter'] = 100000
solver_conf['max_epoch'] = 2000
solver_conf['load_epoch'] = True
solver_conf['phase'] = 'train'
solver_conf['save_freq'] = 20000
solver_conf['print_freq'] = 500
solver_conf['record_fail'] = True

solver_conf['optimizer_name'] = 'SGD'
solver_conf['lr_conf'] = {}
solver_conf['lr_conf']['gen'] = {}
solver_conf['lr_conf']['gen']['decay_type'] = 'poly'
solver_conf['lr_conf']['gen']['poly_base'] = 0.95
solver_conf['lr_conf']['gen']['init_lr'] = 0.01

solver_conf['lr_conf']['dis'] = {}
solver_conf['lr_conf']['dis']['decay_type'] = 'poly'
solver_conf['lr_conf']['dis']['poly_base'] = 0.95
solver_conf['lr_conf']['dis']['init_lr'] = 0.01

loader_conf = {}
loader_conf['solver_name'] = solver_conf['solver_name']
loader_conf['batch_size'] = 8
loader_conf['use_augment'] = True
loader_conf['resize_type'] = 'no_pad'
loader_conf['num_classes'] = 2
loader_conf['num_doms'] = 2
loader_conf['num_workers'] = 4
loader_conf['phase'] = 'train'
loader_conf['load_to_memory'] = False

loader_conf['train_reader_conf'] = {}
loader_conf['train_reader_conf']['file_path'] = '../../Datasets/Inria/train.txt'
loader_conf['train_reader_conf']['root_dir'] = '../../Datasets/Inria'
loader_conf['train_reader_conf']['dataset_type'] = 'mul_dom'
loader_conf['train_reader_conf']['sample_type'] = 'dom'

loader_conf['test_reader_conf'] = {}
loader_conf['test_reader_conf']['file_path'] = '../../Datasets/DeepGlobe/SN2_train_filtered.txt'
loader_conf['test_reader_conf']['root_dir'] = '../../Datasets/DeepGlobe'
loader_conf['test_reader_conf']['dataset_type'] = 'mul_dom'
loader_conf['test_reader_conf']['sample_type'] = 'dom'

loader_conf['dataset_name'] = 'inria2sn2_v2'
loader_conf['dataset_dir'] = '../../Datasets'
loader_conf['img_H'] = 512
loader_conf['img_W'] = 512
loader_conf['num_channels'] = 3
loader_conf['patch_size'] = 512
loader_conf['pad_size'] = 512
loader_conf['random_ratio'] = 0.5
loader_conf['num_used_data'] = 1e8
loader_conf['color'] = True
loader_conf['norm_type'] = 'plain'
loader_conf['A_sample_type'] = 'random'
loader_conf['B_sample_type'] = 'random'
loader_conf['random_type'] = 'city'
loader_conf['aug_conf'] = {'random_rotate': True, 'random_mirror': True, 'random_crop': True,
                           'base_size': [256, 256], 'crop_ratio': [0.5, 2.0], 'crop_size': [256, 256],
                           'resize': True, 'gaussian_blur': True}


## Network Options
net_conf = {}
net_conf['adain_type'] = 'fix_para'
net_conf['dis_step_freq'] = 5
net_conf['use_cls'] = True
net_conf['sha_dec'] = False
net_conf['use_A2M'] = True
net_conf['num_doms'] = 10
net_conf['cls_idx'] = 1
net_conf['use_perc'] = True
net_conf['grad_clip'] = 1
net_conf['margin'] = 0.3
net_conf['use_rgb'] = True
num_in_channels = 3

net_conf['cls_enc_net'] = {}
net_conf['cls_enc_net']['name'] = 'resnet50'
net_conf['cls_enc_net']['depth'] = 5
net_conf['cls_enc_net']['num_in_channels'] = num_in_channels

net_conf['cls_dec_net'] = {}
net_conf['cls_dec_net']['enc_name'] = 'resnet50'
net_conf['cls_dec_net']['enc_channels'] = [3, 64, 256, 512, 1024, 2048]
net_conf['cls_dec_net']['dec_channels'] = [1024, 512, 256, 128, 64]
net_conf['cls_dec_net']['depth'] = 5
net_conf['cls_dec_net']['att_type'] = 'scse'
net_conf['cls_dec_net']['norm_type'] = 'bn'

net_conf['cls_net'] = {}
net_conf['cls_net']['channels'] = [64, 64, loader_conf['num_classes']]
net_conf['cls_net']['activation'] = 'none'
net_conf['cls_net']['norm_type'] = 'in'

net_conf['dis_net'] = {}
net_conf['dis_net']['num_in_channels'] = num_in_channels
net_conf['dis_net']['num_out_channels'] = 64
net_conf['dis_net']['norm_type'] = 'in'
net_conf['dis_net']['use_sn'] = True

net_conf['reg_enc_net'] = {}
net_conf['reg_enc_net']['name'] = 'four_blocks'
net_conf['reg_enc_net']['num_in_channels'] = num_in_channels
net_conf['reg_enc_net']['num_out_channels'] = 64
net_conf['reg_enc_net']['norm_type'] = 'in'
net_conf['reg_enc_net']['use_sn'] = True
net_conf['reg_enc_net']['channels'] = [num_in_channels, 64, 128, 256, 512]

net_conf['reg_dec_net'] = {}
net_conf['reg_dec_net']['name'] = 'unet'
net_conf['reg_dec_net']['enc_name'] = 'four_blocks'
net_conf['reg_dec_net']['enc_channels'] = [num_in_channels, 64, 128, 256, 512]
net_conf['reg_dec_net']['dec_channels'] = [256, 128, 64, 32]
net_conf['reg_dec_net']['depth'] = 4
net_conf['reg_dec_net']['att_type'] = 'scse'
net_conf['reg_dec_net']['norm_type'] = 'in'

net_conf['reg_net'] = {}
net_conf['reg_net']['channels'] = [32, 32, num_in_channels]
net_conf['reg_net']['activation'] = 'none'
net_conf['reg_net']['norm_type'] = 'in'


net_conf['loss_weight_G'] = [50, 50, 1, 5, 1]
net_conf['loss_weight_D'] = [5, 1]

eval_conf = {}
eval_conf['task_type'] = 'seg'
eval_conf['eval_type'] = 'batch'
eval_conf['log_dir'] = solver_conf['log_dir']
eval_conf['dataset_name'] = loader_conf['dataset_name']
eval_conf['num_classes'] = loader_conf['num_classes']
eval_conf['class_names'] = ['others', 'building']

vis_conf = {}
vis_conf['colors'] = [[0,0,0], [255,255,255]]

conf = {'net_conf':net_conf, 'solver_conf':solver_conf, 'loader_conf':loader_conf,
        'eval_conf': eval_conf, 'vis_conf': vis_conf}
