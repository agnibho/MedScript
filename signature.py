# MedScript
# Copyright (C) 2023 Dr. Agnibho Mondal
# This file is part of MedScript.
# MedScript is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# MedScript is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with MedScript. If not, see <https://www.gnu.org/licenses/>.

from M2Crypto import BIO, Rand, SMIME, X509
from config import config
from hashlib import sha256

class Signature():

    def sign(data, certificate, privkey):
        try:
            hash=sha256(data.encode()).hexdigest()
            smime=SMIME.SMIME()
            smime.load_key(privkey, certificate)
            p7=smime.sign(BIO.MemoryBuffer(hash.encode()), SMIME.PKCS7_DETACHED)
            out=BIO.MemoryBuffer()
            smime.write(out, p7)
            return(out.read().decode())
        except Exception as e:
            print(e)
            return None

    def verify(data, certificate, signature):
        hash=sha256(data.encode()).hexdigest()
        smime=SMIME.SMIME()

        x509=X509.load_cert(certificate)
        sk=X509.X509_Stack()
        sk.push(x509)
        smime.set_x509_stack(sk)

        st=X509.X509_Store()
        st.load_info(certificate)
        smime.set_x509_store(st)

        with open(signature) as file:
            buf=BIO.MemoryBuffer(file.read().encode())
        p7=SMIME.smime_load_pkcs7_bio(buf)[0]

        try:
            v=smime.verify(p7, BIO.MemoryBuffer(hash.encode()))
            return(x509.get_subject().as_text())
        except SMIME.PKCS7_Error as e:
            print(e)
            return False
