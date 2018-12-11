# -*- coding: utf-8 -*-

# Copyright 2018 IBM.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# =============================================================================

import numpy as np
import json

from test.common import QiskitAquaTestCase
from qiskit import Aer

from qiskit_aqua import run_algorithm
from qiskit_aqua.input import EnergyInput
from qiskit_aqua.translators.ising import partition
from qiskit_aqua.algorithms.classical import ExactEigensolver


class TestSetPacking(QiskitAquaTestCase):
    """Cplex Ising tests."""

    def setUp(self):
        input_file = self._get_resource_path('sample.partition')
        number_list = partition.read_numbers_from_file(input_file)
        qubitOp, offset = partition.get_partition_qubitops(number_list)
        self.algo_input = EnergyInput(qubitOp)


    def test_partition(self):
        params = {
            'problem': {'name': 'ising'},
            'algorithm': {'name': 'ExactEigensolver'}
        }
        result = run_algorithm(params, self.algo_input)

        x = partition.sample_most_likely(result['eigvecs'][0])
        np.testing.assert_array_equal(x, [0, 1, 0])

    def test_set_packing_direct(self):
        algo = ExactEigensolver(self.algo_input.qubit_op, k=1, aux_operators=[])
        result = algo.run()
        x = partition.sample_most_likely(result['eigvecs'][0])
        np.testing.assert_array_equal(x, [0, 1, 0])


    def test_set_packing_vqe(self):
        algorithm_cfg = {
            'name': 'VQE',
            'operator_mode': 'paulis'

        }

        optimizer_cfg = {
            'name': 'SPSA',
            'max_trials': 200
        }

        var_form_cfg = {
            'name': 'RY',
            'depth': 5,
            'entanglement': 'linear'
        }

        params = {
            'problem': {'name': 'ising', 'random_seed': 100},
            'algorithm': algorithm_cfg,
            'optimizer': optimizer_cfg,
            'variational_form': var_form_cfg
        }
        backend = Aer.get_backend('qasm_simulator')
        result = run_algorithm(params, self.algo_input, backend=backend)
        x = partition.sample_most_likely(result['eigvecs'][0])
        np.testing.assert_array_equal(x, [0, 1, 0])
