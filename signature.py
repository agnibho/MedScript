# MedScript
# Copyright (C) 2023 Dr. Agnibho Mondal
# This file is part of MedScript.
# MedScript is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# MedScript is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with MedScript. If not, see <https://www.gnu.org/licenses/>.

import logging
from config import config
from datetime import datetime
from cryptography.hazmat.primitives.serialization import load_pem_private_key, Encoding
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.x509 import load_pem_x509_certificate

class Signature():

    def sign(data, certificate, privkey, password=""):
        with open(privkey, "rb") as f:
            try:
                priv=load_pem_private_key(f.read(), None, default_backend())
            except TypeError:
                priv=load_pem_private_key(f.read(), password.encode(), default_backend())
        with open(certificate, "rb") as f:
            cert=load_pem_x509_certificate(f.read())
        signature=priv.sign(data.encode(), padding.PKCS1v15(), hashes.SHA256())
        return signature

    def verify(data, certificate, signature):
        try:
            if(not Signature.verify_chain(certificate)):
                return False
        except Exception as e:
            logging.warning(e)
            return False

        with open(certificate, "rb") as f:
            cert=load_pem_x509_certificate(f.read())
        pub=cert.public_key()
        try:
            pub.verify(signature, data.encode(), padding.PKCS1v15(), hashes.SHA256())
            subattr=""
            for i in cert.subject:
                subattr+=i.oid._name+":"+i.value+"\n"
            return subattr
        except Exception as e:
            logging.warning(e)
            return False

    def verify_chain(cert_chain_path):
        cert_chain=[]
        with open(cert_chain_path) as chain_file:
            cert_data=""
            for line in chain_file:
                cert_data=cert_data+line.strip()+"\n"
                if "----END CERTIFICATE----" in line:
                    cert_chain.append(load_pem_x509_certificate(cert_data.encode()))
                    cert_data=""

        for i in range(len(cert_chain)):
            cert=cert_chain[i]
            if(datetime.utcnow().timestamp()>cert.not_valid_after.timestamp()):
                logging.warning("Certificate expired")
                return False
            if(i>0):
                prev_cert=cert_chain[i-1]
                try:
                    cert.public_key().verify(prev_cert.signature, prev_cert.tbs_certificate_bytes, padding.PKCS1v15(), prev_cert.signature_hash_algorithm)
                except InvalidSignature:
                    logging.warning("Certificate chain signature verification failed")
                    return False
        try:
            with open(config["root_bundle"]) as root:
                root_bundle=root.read()
            if(cert_chain[-1].public_bytes(encoding=Encoding.PEM).decode() not in root_bundle):
                logging.warning("Certificate not in root bundle")
                return False
            return True
        except Exception as e:
            logging.warning(e)
            logging.warning("Root bundle could not be loaded")
            return False
