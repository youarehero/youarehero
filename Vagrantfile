# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "precise64"
  config.vm.box_url = "http://files.vagrantup.com/precise64.box"

  config.vm.hostname = "youarehero.vagrant"
  config.vm.network :private_network, ip: "192.168.33.10"
  config.vm.network :forwarded_port, guest: 80, host: 8000

  config.vm.synced_folder ".", "/vagrant", extra: "dmode=555,fmode=555"

  config.vm.provider :virtualbox do |vb|
    vb.customize ['guestproperty', 'set', :id, '/VirtualBox/GuestAdd/VBoxService/--timesync-interval', '500']
    vb.customize ['guestproperty', 'set', :id, '/VirtualBox/GuestAdd/VBoxService/--timesync-set-threshold', '800']
  end

  config.vm.provision :ansible do |ansible|
    ansible.playbook = "provisioning/youarehero.yml"
    ansible.inventory_file = "provisioning/ansible_hosts"
  end
end
