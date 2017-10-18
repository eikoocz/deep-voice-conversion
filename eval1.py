# -*- coding: utf-8 -*-
# /usr/bin/python2

from __future__ import print_function

from data_load import *
from models import Model
import argparse
from hyperparams import logdir_path


def eval(logdir='logdir/train1', queue=True):
    # Load graph
    model = Model(mode="test1", batch_size=hp.test1.batch_size, queue=queue)

    # Accuracy
    acc_op = model.acc_net1()

    # Loss
    loss_op = model.loss_net1()

    # Summary
    summ_op = summaries(acc_op, loss_op)

    session_conf = tf.ConfigProto(
        allow_soft_placement=True,
        device_count={'CPU': 1, 'GPU': 0},
    )
    with tf.Session(config=session_conf) as sess:
        coord = tf.train.Coordinator()
        threads = tf.train.start_queue_runners(coord=coord)

        writer = tf.summary.FileWriter(logdir, sess.graph)

        # Load trained model
        sess.run(tf.global_variables_initializer())
        model.load(sess, 'train1', logdir=logdir)

        if queue:
            summ, acc, loss = sess.run([summ_op, acc_op, loss_op])
        else:
            x, y = get_batch(model.mode, model.batch_size)
            summ, acc, loss = sess.run([summ_op, acc_op, loss_op], feed_dict={model.x_mfcc: x, model.y_ppgs: y})

        writer.add_summary(summ)

        print("acc:", acc)
        print("loss:", loss)
        print('\n')

        writer.close()

        coord.request_stop()
        coord.join(threads)


def summaries(acc, loss):
    tf.summary.scalar('net1/eval/acc', acc)
    tf.summary.scalar('net1/eval/loss', loss)
    return tf.summary.merge_all()


def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('logdir', type=str, help='logdir path', default='{}/logdir/train1'.format(logdir_path))
    arguments = parser.parse_args()
    return arguments


if __name__ == '__main__':
    args = get_arguments()
    eval(logdir=args.logdir)
    print("Done")
